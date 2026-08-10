/*
Settings tab: a read/write view of the key config values plus entry points
for the wizard, health check, and token re-application. The full answer set
lives in qms.config.json; the wizard is the intended editor for scope.
*/
import { App, PluginSettingTab, Setting } from "obsidian";
import type MicroQmsPlugin from "./main";
import { DocControlMode } from "./config";
import { HARVEST_COMMIT } from "./generated/templates";

export class MicroQmsSettingTab extends PluginSettingTab {
  private plugin: MicroQmsPlugin;

  constructor(app: App, plugin: MicroQmsPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();
    const config = this.plugin.config;

    new Setting(containerEl)
      .setName("Organisation")
      .setDesc("Change via the setup wizard so documents are updated consistently.")
      .addText((t) => t.setValue(config.organisation).setDisabled(true));

    new Setting(containerEl).setName("Quality manager").addText((t) =>
      t.setValue(config.quality_manager).onChange(async (v) => {
        config.quality_manager = v.trim();
        await this.plugin.saveQmsConfig();
      }),
    );

    new Setting(containerEl)
      .setName("Document control mode")
      .setDesc(
        this.plugin.gitDetected
          ? "A git repository was detected in this vault."
          : "No git repository detected; shared-drive mode is recommended.",
      )
      .addDropdown((d) => {
        d.addOption("shared-drive", "Shared drive (plugin-managed)");
        d.addOption("git", "Git (annotated-tag ceremony)");
        d.setValue(config.doc_control_mode).onChange(async (v) => {
          config.doc_control_mode = v as DocControlMode;
          await this.plugin.saveQmsConfig();
        });
      });

    new Setting(containerEl)
      .setName("Setup wizard")
      .setDesc(
        config.wizard_completed_at
          ? `Last completed ${config.wizard_completed_at.slice(0, 10)}. Re-running is safe: answers are kept and content is not overwritten.`
          : "Not yet run for this vault.",
      )
      .addButton((b) => b.setButtonText("Run setup wizard").setCta().onClick(() => this.plugin.openWizard()));

    new Setting(containerEl)
      .setName("QMS health check")
      .setDesc("Quick in-vault validation of folders, frontmatter, and approval fields.")
      .addButton((b) => b.setButtonText("Run health check").onClick(() => this.plugin.runHealthCheck()));

    new Setting(containerEl)
      .setName("Bundled template revision")
      .setDesc(`Documents are scaffolded from lean-iso13485-qms commit ${HARVEST_COMMIT}.`)
      .addButton((b) => b.setButtonText("Re-apply tokens").onClick(() => this.plugin.reapplyTokens()));
  }
}
