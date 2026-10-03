import logging
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.consumer import Consumer
from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.producer import Producer
from app.models.semantic_rule import SemanticRule
from app.schemas.contract import (
    ContractCreate,
    ContractDetailResponse,
    ContractResponse,
)
from app.schemas.contract_version import (
    ContractVersionCreate,
    ContractVersionResponse,
)
from app.schemas.compatibility import (
    CompatibilityCheckRequest,
    CompatibilityReportResponse,
)
from app.schemas.semantic_rule import (
    SemanticRuleResponse,
    SemanticValidationResponse,
)
from app.schemas.lineage import ContractLineageResponse
from app.schemas.impact_analysis import (
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
)
from app.schemas.runtime_validation import RuntimeValidationResponse
from app.services.compatibility import CompatibilityEngine
from app.services.impact_analysis import (
    ContractNotFoundError,
    ImpactAnalysisService,
    SameVersionError,
    VersionNotFoundError,
)
from app.services.lineage import LineageService
from app.services.runtime_validator import (
    RuntimeValidationService,
    ContractNotFoundError as RuntimeContractNotFoundError,
    VersionNotFoundError as RuntimeVersionNotFoundError,
)
from app.services.semantic_validator import SemanticValidationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("", response_model=ContractDetailResponse, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)) -> Contract:
    """Create a new data contract between a producer and optional consumers."""
    producer = db.query(Producer).filter(Producer.id == payload.producer_id).first()
    if not producer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producer with ID {payload.producer_id} does not exist.",
        )

    existing = db.query(Contract).filter(Contract.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contract with name '{payload.name}' already exists.",
        )

    consumers: list[Consumer] = []
    if payload.consumer_ids:
        consumers = db.query(Consumer).filter(Consumer.id.in_(payload.consumer_ids)).all()
        found_ids = {c.id for c in consumers}
        missing_ids = set(payload.consumer_ids) - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consumer(s) with ID(s) {sorted(missing_ids)} do not exist.",
            )

    contract = Contract(
        name=payload.name,
        description=payload.description,
        producer_id=payload.producer_id,
        consumers=consumers,
    )
    try:
        db.add(contract)
        db.commit()
        db.refresh(contract)
        logger.info("Successfully registered contract id=%d name='%s' producer_id=%d", contract.id, contract.name, contract.producer_id)
        return contract
    except IntegrityError:
        db.rollback()
        logger.warning("Conflict creating contract: name '%s' already exists", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contract with name '{payload.name}' already exists.",
        )


@router.get("", response_model=list[ContractResponse])
def list_contracts(db: Session = Depends(get_db)) -> list[Contract]:
    """Retrieve all registered contracts."""
    return db.query(Contract).order_by(Contract.id).all()


@router.get("/{id}", response_model=ContractDetailResponse)
def get_contract(id: int, db: Session = Depends(get_db)) -> Contract:
    """Retrieve full details of a specific contract including producer, consumers, and versions."""
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )
    return contract


@router.post("/{id}/versions", response_model=ContractVersionResponse, status_code=status.HTTP_201_CREATED)
def create_contract_version(
    id: int,
    payload: ContractVersionCreate,
    db: Session = Depends(get_db),
) -> ContractVersion:
    """Register a new schema version for a specific contract."""
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )

    existing_version = (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == id, ContractVersion.version_number == payload.version_number)
        .first()
    )
    if existing_version:
        logger.warning("Conflict creating version: version %d already exists for contract id=%d", payload.version_number, id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version {payload.version_number} already exists for contract ID {id}.",
        )

    version = ContractVersion(
        contract_id=id,
        version_number=payload.version_number,
        schema_definition=payload.schema_definition,
        description=payload.description,
    )
    try:
        db.add(version)
        db.commit()
        db.refresh(version)
        logger.info("Successfully registered version %d for contract id=%d", version.version_number, id)
        return version
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error registering version %d for contract id=%d", payload.version_number, id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version {payload.version_number} already exists for contract ID {id}.",
        )


@router.get("/{id}/versions", response_model=list[ContractVersionResponse])
def list_contract_versions(id: int, db: Session = Depends(get_db)) -> list[ContractVersion]:
    """List all schema versions registered under a contract."""
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )
    return (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == id)
        .order_by(ContractVersion.version_number)
        .all()
    )


@router.get("/{id}/versions/{version}", response_model=ContractVersionResponse)
def get_contract_version(id: int, version: int, db: Session = Depends(get_db)) -> ContractVersion:
    """Retrieve an individual schema version specification for a contract."""
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )

    contract_version = (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == id, ContractVersion.version_number == version)
        .first()
    )
    if not contract_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found for contract ID {id}.",
        )
    return contract_version


@router.post(
    "/{id}/compatibility",
    response_model=CompatibilityReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate schema compatibility between two versions of a contract",
)
def check_compatibility(
    id: int,
    payload: CompatibilityCheckRequest,
    db: Session = Depends(get_db),
) -> CompatibilityReportResponse:
    """Evaluate schema compatibility between two versions of the same contract.

    Compares the schema at `old_version` with `new_version` according to
    Contract Guard compatibility policies and returns detailed findings.
    """
    # 1. Verify contract exists
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )

    # 2. Verify distinct versions
    if payload.old_version == payload.new_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="old_version and new_version must be distinct version numbers.",
        )

    # 3. Verify old_version exists
    v_old = (
        db.query(ContractVersion)
        .filter(
            ContractVersion.contract_id == id,
            ContractVersion.version_number == payload.old_version,
        )
        .first()
    )
    if not v_old:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {payload.old_version} not found for contract ID {id}.",
        )

    # 4. Verify new_version exists
    v_new = (
        db.query(ContractVersion)
        .filter(
            ContractVersion.contract_id == id,
            ContractVersion.version_number == payload.new_version,
        )
        .first()
    )
    if not v_new:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {payload.new_version} not found for contract ID {id}.",
        )

    # 5. Evaluate on demand
    logger.info("Evaluating compatibility for contract id=%d: v%d -> v%d", id, payload.old_version, payload.new_version)
    return CompatibilityEngine.compare_schemas(
        old_schema=v_old.schema_definition,
        new_schema=v_new.schema_definition,
        old_version=payload.old_version,
        new_version=payload.new_version,
        contract_id=contract.id,
        contract_name=contract.name,
    )


@router.post(
    "/{id}/semantic-validation",
    response_model=SemanticValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate a data payload sample against contract semantic rules",
)
def validate_contract_semantics(
    id: int,
    sample: dict[str, Any] = Body(..., description="JSON payload data sample to validate"),
    db: Session = Depends(get_db),
) -> SemanticValidationResponse:
    """Validate a data sample against all semantic/business rules defined for a contract.

    Evaluates rules such as value bounds (>= 0) and allowed enumeration values.
    Returns structured pass/fail results and itemized violations.
    """
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )

    rules = (
        db.query(SemanticRule)
        .filter(SemanticRule.contract_id == id)
        .order_by(SemanticRule.id)
        .all()
    )

    logger.info("Executing semantic validation for contract id=%d (%d rules configured)", id, len(rules))
    return SemanticValidationEngine.validate_sample(
        rules=rules,
        sample=sample,
        contract_id=contract.id,
        contract_name=contract.name,
    )


@router.get(
    "/{id}/semantic-rules",
    response_model=list[SemanticRuleResponse],
    status_code=status.HTTP_200_OK,
    summary="List all semantic rules configured for a contract",
)
def list_contract_semantic_rules(
    id: int,
    db: Session = Depends(get_db),
) -> list[SemanticRule]:
    """Retrieve all semantic business rules defined for a contract."""
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )

    return (
        db.query(SemanticRule)
        .filter(SemanticRule.contract_id == id)
        .order_by(SemanticRule.id)
        .all()
    )


@router.get(
    "/{id}/lineage",
    response_model=ContractLineageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get producer-to-consumer lineage for a contract",
)
def get_contract_lineage(
    id: int,
    db: Session = Depends(get_db),
) -> ContractLineageResponse:
    """Retrieve lineage for a specific contract.

    Returns the producing system and all consuming systems registered for the contract.
    """
    lineage = LineageService.get_contract_lineage(db=db, contract_id=id)
    if not lineage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {id} not found.",
        )
    logger.info("Retrieved lineage for contract id=%d", id)
    return lineage


@router.post(
    "/{id}/impact-analysis",
    response_model=ImpactAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze downstream impact of contract schema evolution",
)
def analyze_contract_impact(
    id: int,
    payload: ImpactAnalysisRequest,
    db: Session = Depends(get_db),
) -> ImpactAnalysisResponse:
    """Analyze downstream consumer impact caused by evolving a contract schema.

    Combines compatibility check results with contract lineage to determine which
    downstream consumers will be affected if the contract transitions from old_version
    to new_version.
    """
    try:
        logger.info("Analyzing impact for contract id=%d: v%d -> v%d", id, payload.old_version, payload.new_version)
        return ImpactAnalysisService.analyze_impact(
            db=db,
            contract_id=id,
            old_version=payload.old_version,
            new_version=payload.new_version,
        )
    except SameVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except (ContractNotFoundError, VersionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{id}/versions/{version}/validate",
    response_model=RuntimeValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate runtime data sample against contract version schema and semantic rules",
)
def validate_runtime_sample(
    id: int = Path(..., description="ID of the contract"),
    version: int = Path(..., gt=0, description="Version number of the contract"),
    sample: dict[str, Any] = Body(..., description="Runtime JSON sample payload to validate"),
    db: Session = Depends(get_db),
) -> RuntimeValidationResponse:
    """Validate a runtime data payload against a specific contract version's schema and semantic rules.

    Performs two-tier validation:
    1. JSON Schema validation against the contract version's schema definition.
    2. Semantic rule validation against all business rules defined for the contract.

    Returns detailed findings for both tiers, and overall valid=True only if both pass.
    """
    try:
        logger.info("Executing runtime sample validation for contract id=%d version=%d", id, version)
        return RuntimeValidationService.validate_runtime_sample(
            db=db,
            contract_id=id,
            version_number=version,
            sample=sample,
        )
    except (RuntimeContractNotFoundError, RuntimeVersionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

