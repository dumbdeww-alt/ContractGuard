import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:5173";

test.describe("ContractGuard Contracts", () => {
  test("Contracts page loads correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/contracts`);

    await expect(page.locator("body")).toContainText("Student Contract");
    await expect(page.locator("body")).toContainText("Attendance Contract");
    await expect(page.locator("body")).toContainText("Exam Contract");
  });

  test("Impact button opens Impact Analysis", async ({ page }) => {
    await page.goto(`${BASE_URL}/contracts`);

    await page.getByRole("button", { name: "Impact", exact: true }).first().click();

    await expect(page.locator("body")).toContainText("Impact Analysis");
  });

  test("Alerts button opens Breaking Change Alerts", async ({ page }) => {
    await page.goto(`${BASE_URL}/contracts`);

    await page.getByRole("button", { name: "Alerts", exact: true }).first().click();

    await expect(page.locator("body")).toContainText(
      "Breaking Change Alerts"
    );
  });

  test("Review button opens Approval Workflow", async ({ page }) => {
    await page.goto(`${BASE_URL}/contracts`);

    await page.getByRole("button", { name: "Review", exact: true }).first().click();

    await expect(page.locator("body")).toContainText("Approval Workflow");
  });

  test("Validate button opens Runtime Validation", async ({ page }) => {
    await page.goto(`${BASE_URL}/contracts`);

    await page
      .getByRole("button", { name: "Validate", exact: true })
      .first()
      .click();

    await expect(page.locator("body")).toContainText("Runtime Validation");
  });
});