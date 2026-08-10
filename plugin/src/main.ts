/*
Micro QMS - plugin entry point. Registers the setup wizard, document
lifecycle commands, and the health check. The vault's qms.config.json (shared
with the repository's Python tooling) is the single source of configuration;
Obsidian's own plugin data store is not used.
*/
import { Menu, Notice, Plugin, TFile } from "obsidian";
import { loadConfig, QmsConfig, saveConfig } from "./config";
import { detectGitRepo, GitCeremonyModal } from "./gitmode";
import { HealthCheckModal, runHealthCheck } from "./healthcheck";
import {
  approveDocument,
  FieldPromptModal,
  markObsolete,
  readDocInfo,
  startNewRevision,
  submitForReview,
  todayIso,
} from "./lifecycle";
import { scaffoldVault } from "./scaffold";
import { MicroQmsSettingTab } from "./settings";
import { SetupWizardModal } from "./wizard/wizard";

export default class MicroQmsPlugin extends Plugin {
  config!: QmsConfig;
  gitDetected = false;

  async onload(): Promise<void> {
    this.config = await loadConfig(this.app);
    this.gitDetected = await detectGitRepo(this.app);

    this.addSettingTab(new MicroQmsSettingTab(this.app, this));

    this.addCommand({
      id: "setup-wizard",
      name: "Run setup wizard",
      callback: () => this.openWizard(),
    });

    this.addCommand({
      id: "health-check",
      name: "Run QMS health check",
      callback: () => this.runHealthCheck(),
    });

    this.addCommand({
      id: "reapply-tokens",
      name: "Re-apply personalisation tokens",
      callback: () => this.reapplyTokens(),
    });

    this.addCommand({
      id: "submit-for-review",
      name: "Submit document for review",
      checkCallback: (checking) => this.withActiveDoc(checking, (f) => this.promptSubmitForReview(f)),
    });

    this.addCommand({
      id: "approve-document",
      name: "Approve document",
      checkCallback: (checking) => this.withActiveDoc(checking, (f) => this.promptApprove(f)),
    });

    this.addCommand({
      id: "new-revision",
      name: "Start new revision of approved document",
      checkCallback: (checking) => this.withActiveDoc(checking, (f) => startNewRevision(this.app, f)),
    });

    this.addCommand({
      id: "mark-obsolete",
      name: "Mark document obsolete (move to archive)",
      checkCallback: (checking) => this.withActiveDoc(checking, (f) => this.promptObsolete(f)),
    });

    this.registerEvent(
      this.app.workspace.on("file-menu", (menu: Menu, file) => {
        if (!(file instanceof TFile) || file.extension !== "md") return;
        menu.addItem((item) =>
          item
            .setTitle("Micro QMS: approve document")
            .setIcon("check-circle")
            .onClick(() => this.promptApprove(file)),
        );
        menu.addItem((item) =>
          item
            .setTitle("Micro QMS: start new revision")
            .setIcon("git-branch")
            .onClick(() => startNewRevision(this.app, file)),
        );
      }),
    );
  }

  private withActiveDoc(checking: boolean, action: (file: TFile) => void): boolean {
    const file = this.app.workspace.getActiveFile();
    if (!file || file.extension !== "md") return false;
    if (!checking) action(file);
    return true;
  }

  async saveQmsConfig(): Promise<void> {
    await saveConfig(this.app, this.config);
  }

  openWizard(): void {
    new SetupWizardModal(this.app, this.config, this.gitDetected, async () => {
      this.config = await loadConfig(this.app);
    }).open();
  }

  async runHealthCheck(): Promise<void> {
    const results = await runHealthCheck(this.app);
    new HealthCheckModal(this.app, results).open();
  }

  /* Re-run the scaffolder: fills tokens and re-derives the QM-04 table from
     the stored config without touching document prose. */
  async reapplyTokens(): Promise<void> {
    const report = await scaffoldVault(this.app, this.config);
    new Notice(
      `Micro QMS: ${report.docsUpdated.length} document(s) updated, ${report.docsCreated.length} created.`,
    );
  }

  private promptSubmitForReview(file: TFile): void {
    new FieldPromptModal(
      this.app,
      "Submit for review",
      [{ name: "Reviewer", desc: "Who will review this document?", initial: this.config.quality_manager }],
      ([reviewer]) => void submitForReview(this.app, file, reviewer.trim()),
    ).open();
  }

  private async promptApprove(file: TFile): Promise<void> {
    if (this.config.doc_control_mode === "git") {
      const info = await readDocInfo(this.app, file);
      if (!info) {
        new Notice("Not a controlled document (missing doc_id/revision/status frontmatter).");
        return;
      }
      new GitCeremonyModal(this.app, info, file.path).open();
      return;
    }
    new FieldPromptModal(
      this.app,
      "Approve document",
      [
        { name: "Approver", desc: "Name recorded as approver.", initial: this.config.quality_manager },
        { name: "Effective date", desc: "YYYY-MM-DD.", initial: todayIso() },
      ],
      ([approver, date]) => void approveDocument(this.app, file, approver, date.trim()),
    ).open();
  }

  private promptObsolete(file: TFile): void {
    new FieldPromptModal(
      this.app,
      "Mark obsolete",
      [{ name: "Type OBSOLETE to confirm", desc: "The document moves to _archive/.", initial: "" }],
      ([confirm]) => {
        if (confirm.trim().toUpperCase() === "OBSOLETE") {
          void markObsolete(this.app, file);
        } else {
          new Notice("Cancelled: confirmation text did not match.");
        }
      },
    ).open();
  }
}
