/*
Setup wizard: a four-step modal. Answers accumulate in a draft config and
nothing is written until Apply on the final step, which saves qms.config.json
and runs the scaffolder. Re-running the wizard loads the saved answers, so
setup is repeatable and non-destructive.
*/
import { App, Modal, Notice, Setting } from "obsidian";
import { DEFAULT_ORG, DocControlMode, QmsConfig, REGULATORY_ROLE_LABELS, RegulatoryRole, saveConfig } from "../config";
import { deriveExclusions, scaffoldVault, ScaffoldReport } from "../scaffold";
import { BUNDLED_DOCS, HARVEST_COMMIT } from "../generated/templates";
import { defaultJustificationFor, formatSites, parseLines, parseSites, SCOPE_QUESTIONS } from "./steps";

const MARKET_OPTIONS = ["EU", "US", "UK"];

export class SetupWizardModal extends Modal {
  private draft: QmsConfig;
  private step = 0;
  private gitDetected: boolean;
  private onDone: (report: ScaffoldReport) => void;

  constructor(app: App, initial: QmsConfig, gitDetected: boolean, onDone: (report: ScaffoldReport) => void) {
    super(app);
    // Deep-clone so cancelling leaves the stored config untouched.
    this.draft = JSON.parse(JSON.stringify(initial));
    if (this.gitDetectedDefaultNeeded(initial)) {
      this.draft.doc_control_mode = gitDetected ? "git" : "shared-drive";
    }
    this.gitDetected = gitDetected;
    this.onDone = onDone;
  }

  private gitDetectedDefaultNeeded(initial: QmsConfig): boolean {
    return !initial.wizard_completed_at;
  }

  onOpen(): void {
    this.render();
  }

  private render(): void {
    const { contentEl } = this;
    contentEl.empty();
    const titles = ["Company details", "Scope of the QMS", "Document control mode", "Review and apply"];
    contentEl.createEl("h2", { text: `Micro QMS setup - ${titles[this.step]}`, cls: "microqms-wizard-step-title" });
    contentEl.createEl("div", { text: `Step ${this.step + 1} of ${titles.length}`, cls: "microqms-wizard-step-count" });

    switch (this.step) {
      case 0:
        this.renderCompanyStep(contentEl);
        break;
      case 1:
        this.renderScopeStep(contentEl);
        break;
      case 2:
        this.renderModeStep(contentEl);
        break;
      case 3:
        this.renderReviewStep(contentEl);
        break;
    }
    this.renderNav(contentEl);
  }

  private renderCompanyStep(el: HTMLElement): void {
    new Setting(el)
      .setName("Organisation name")
      .setDesc("The legal entity operating the QMS. Required.")
      .addText((t) =>
        t.setValue(this.draft.organisation === DEFAULT_ORG ? "" : this.draft.organisation).onChange((v) => {
          this.draft.organisation = v.trim() || DEFAULT_ORG;
        }),
      );
    new Setting(el)
      .setName("Quality manager")
      .setDesc("The appointed management representative (section 5.5.2).")
      .addText((t) => t.setValue(this.draft.quality_manager).onChange((v) => (this.draft.quality_manager = v.trim())));
    new Setting(el)
      .setName("Company registration number")
      .addText((t) =>
        t.setValue(this.draft.company.registration_number).onChange((v) => (this.draft.company.registration_number = v.trim())),
      );
    new Setting(el)
      .setName("Registered office")
      .addText((t) =>
        t.setValue(this.draft.company.registered_office).onChange((v) => (this.draft.company.registered_office = v.trim())),
      );
    new Setting(el)
      .setName("Operating sites")
      .setDesc("One per line: address | activities performed there.")
      .addTextArea((t) =>
        t.setValue(formatSites(this.draft.company.operating_sites)).onChange((v) => {
          this.draft.company.operating_sites = parseSites(v);
        }),
      );
    new Setting(el)
      .setName("Device types")
      .setDesc("One per line, e.g. single-use surgical instruments.")
      .addTextArea((t) =>
        t.setValue(this.draft.company.device_types.join("\n")).onChange((v) => {
          this.draft.company.device_types = parseLines(v);
        }),
      );
    new Setting(el).setName("Regulatory role").addDropdown((d) => {
      for (const [value, label] of Object.entries(REGULATORY_ROLE_LABELS)) d.addOption(value, label);
      d.setValue(this.draft.company.regulatory_role).onChange((v) => {
        this.draft.company.regulatory_role = v as RegulatoryRole;
      });
    });
    for (const market of MARKET_OPTIONS) {
      new Setting(el).setName(`Market: ${market}`).addToggle((t) =>
        t.setValue(this.draft.company.markets.includes(market)).onChange((on) => {
          const set = new Set(this.draft.company.markets);
          if (on) set.add(market);
          else set.delete(market);
          this.draft.company.markets = [...MARKET_OPTIONS.filter((m) => set.has(m)), ...[...set].filter((m) => !MARKET_OPTIONS.includes(m))];
        }),
      );
    }
    new Setting(el)
      .setName("Other markets")
      .setDesc("Comma-separated, e.g. Canada, Australia.")
      .addText((t) =>
        t
          .setValue(this.draft.company.markets.filter((m) => !MARKET_OPTIONS.includes(m)).join(", "))
          .onChange((v) => {
            const others = v.split(",").map((s) => s.trim()).filter(Boolean);
            const std = this.draft.company.markets.filter((m) => MARKET_OPTIONS.includes(m));
            this.draft.company.markets = [...std, ...others];
          }),
      );
  }

  private renderScopeStep(el: HTMLElement): void {
    el.createEl("p", {
      text:
        "Answer for what the organisation actually does. A 'no' on a clause-linked question records that clause " +
        "as not applicable in QM-04 with your justification; do not exclude a clause because it is inconvenient.",
    });
    for (const q of SCOPE_QUESTIONS) {
      const setting = new Setting(el).setName(q.question).setDesc(q.detail).setClass("microqms-wizard-question");
      setting.addToggle((t) =>
        t.setValue(this.draft.scope[q.key]).onChange((on) => {
          this.draft.scope[q.key] = on;
          this.render();
        }),
      );
      if (q.clause && !this.draft.scope[q.key]) {
        const stored = this.draft.clause_exclusions[q.clause];
        const value = (stored && !stored.applicable && stored.justification) || defaultJustificationFor(q.clause);
        new Setting(el)
          .setName(`Justification for excluding clause ${q.clause}`)
          .setClass("microqms-wizard-justification")
          .addTextArea((t) =>
            t.setValue(value).onChange((v) => {
              this.draft.clause_exclusions[q.clause as string] = { applicable: false, justification: v.trim() };
            }),
          );
        if (!stored || stored.applicable) {
          this.draft.clause_exclusions[q.clause] = { applicable: false, justification: value };
        }
      } else if (q.clause) {
        this.draft.clause_exclusions[q.clause] = { applicable: true, justification: "" };
      }
    }
    new Setting(el)
      .setName("Outsourced processes")
      .setDesc("One per line, e.g. sterilisation, PCB assembly. Leave empty if none.")
      .addTextArea((t) =>
        t.setValue(this.draft.scope.outsourced_processes.join("\n")).onChange((v) => {
          this.draft.scope.outsourced_processes = parseLines(v);
        }),
      );
  }

  private renderModeStep(el: HTMLElement): void {
    el.createEl("p", {
      text: this.gitDetected
        ? "A git repository was detected in this vault. Git mode keeps the annotated-tag approval ceremony " +
          "(the plugin shows you the commands instead of changing files silently)."
        : "No git repository was detected. Shared-drive mode manages document status, approval dates, and the " +
          "archive folder directly in the vault, which suits a synced folder such as Dropbox, Google Drive, or SharePoint.",
    });
    new Setting(el).setName("Document control mode").addDropdown((d) => {
      d.addOption("shared-drive", "Shared drive (plugin-managed)");
      d.addOption("git", "Git (annotated-tag ceremony)");
      d.setValue(this.draft.doc_control_mode).onChange((v) => {
        this.draft.doc_control_mode = v as DocControlMode;
      });
    });
  }

  private renderReviewStep(el: HTMLElement): void {
    const exclusions = deriveExclusions(this.draft);
    const excluded = Object.entries(exclusions).filter(([, e]) => !e.applicable);
    const preview = el.createDiv({ cls: "microqms-preview" });
    preview.createEl("strong", { text: `Organisation: ${this.draft.organisation}` });
    const list = preview.createEl("ul");
    list.createEl("li", { text: `Quality manager: ${this.draft.quality_manager || "(not set)"}` });
    list.createEl("li", { text: `Devices: ${this.draft.company.device_types.join(", ") || "(not set)"}` });
    list.createEl("li", { text: `Markets: ${this.draft.company.markets.join(", ") || "(not set)"}` });
    list.createEl("li", { text: `Document control: ${this.draft.doc_control_mode}` });
    list.createEl("li", { text: `Documents in bundle: ${BUNDLED_DOCS.length} (template revision ${HARVEST_COMMIT})` });
    preview.createEl("strong", { text: "Clause applicability (QM-04):" });
    const clauseList = preview.createEl("ul");
    if (excluded.length === 0) {
      clauseList.createEl("li", { text: "All conditional clauses applicable." });
    }
    for (const [clause, e] of excluded) {
      clauseList.createEl("li", { text: `${clause}: N/A - ${e.justification}` });
    }
    el.createEl("p", {
      text:
        "Apply writes qms.config.json, creates any missing folders and documents, fills the personalisation " +
        "tokens, and updates the QM-04 applicability table. Existing document content is not overwritten.",
    });
  }

  private renderNav(el: HTMLElement): void {
    const nav = el.createDiv({ cls: "microqms-wizard-nav" });
    if (this.step > 0) {
      const back = nav.createEl("button", { text: "Back" });
      back.addEventListener("click", () => {
        this.step--;
        this.render();
      });
    }
    const next = nav.createEl("button", { text: this.step === 3 ? "Apply" : "Next", cls: "mod-cta" });
    next.addEventListener("click", async () => {
      if (this.step === 0 && (!this.draft.organisation || this.draft.organisation === DEFAULT_ORG)) {
        new Notice("Organisation name is required.");
        return;
      }
      if (this.step < 3) {
        this.step++;
        this.render();
        return;
      }
      await this.apply();
    });
  }

  private async apply(): Promise<void> {
    this.draft.clause_exclusions = deriveExclusions(this.draft);
    this.draft.wizard_completed_at = new Date().toISOString();
    await saveConfig(this.app, this.draft);
    const report = await scaffoldVault(this.app, this.draft);
    this.close();
    new Notice(
      `Micro QMS: ${report.docsCreated.length} documents created, ${report.docsUpdated.length} updated.` +
        (report.warnings.length ? ` ${report.warnings.length} warning(s).` : ""),
      8000,
    );
    for (const w of report.warnings) new Notice(w, 10000);
    this.onDone(report);
  }

  onClose(): void {
    this.contentEl.empty();
  }
}
