/*
Git document-control mode. The plugin never runs git itself: the approval
ceremony (annotated tags as approval evidence) belongs to the Makefile and the
human. In git mode the approve command opens this modal showing the exact
commands, with copy-to-clipboard.
*/
import { App, Modal, Notice } from "obsidian";
import { DocInfo } from "./lifecycle";

export async function detectGitRepo(app: App): Promise<boolean> {
  return app.vault.adapter.exists(".git");
}

export class GitCeremonyModal extends Modal {
  private info: DocInfo;
  private filePath: string;

  constructor(app: App, info: DocInfo, filePath: string) {
    super(app);
    this.info = info;
    this.filePath = filePath;
  }

  onOpen(): void {
    const { contentEl } = this;
    contentEl.addClass("microqms-ceremony");
    contentEl.createEl("h3", { text: `Approve ${this.info.docId} Rev ${this.info.revision} (git mode)` });
    contentEl.createEl("p", {
      text:
        "This vault uses git as the document-control system, so approval is a commit plus an annotated tag " +
        "rather than a plugin action. Set the approval frontmatter first (status, effective_date, review_due, " +
        "approved_date), quit Obsidian if the git plugin is active, then run:",
    });
    const commands = [
      `git add "${this.filePath}"`,
      `git commit -m "${this.info.docId}: approve - Rev ${this.info.revision}"`,
      `make approve DOC=${this.info.docId} REV=${this.info.revision}`,
      `make push`,
      `make validate`,
    ].join("\n");
    contentEl.createEl("pre", { text: commands });
    const btn = contentEl.createEl("button", { text: "Copy commands", cls: "mod-cta" });
    btn.addEventListener("click", async () => {
      await navigator.clipboard.writeText(commands);
      new Notice("Commands copied to clipboard.");
    });
    contentEl.createEl("p", {
      text: "HOWTO.md section 3 walks through the full ceremony, including the validation record.",
    });
  }

  onClose(): void {
    this.contentEl.empty();
  }
}
