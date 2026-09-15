const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
function inside(base, target) {
  const rel = path.relative(base, target);
  return rel && !rel.startsWith('..') && !path.isAbsolute(rel);
}
function write(file, obj) {
  fs.writeFileSync(file + '.tmp', JSON.stringify(obj, null, 2));
  fs.renameSync(file + '.tmp', file);
}
function escapeXml(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}
function activate(context) {
  let busy = false;
  context.subscriptions.push(vscode.window.registerUriHandler({
    async handleUri(uri) {
      const requestFile = new URLSearchParams(uri.query).get('request');
      if (!requestFile || !vscode.workspace.isTrusted) return;
      const realRequest = fs.realpathSync(requestFile);
      const workspace = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(realRequest));
      if (!workspace) throw new Error('Open the ATS project in this VS Code window first.');
      const root = fs.realpathSync(workspace.uri.fsPath);
      if (!inside(path.join(root, 'usbupdate', 'logs'), realRequest) || path.basename(realRequest) !== 'ats-request.json') return;
      const request = JSON.parse(fs.readFileSync(realRequest, 'utf8'));
      const directory = path.dirname(realRequest);
      const response = path.join(directory, 'ats-result.json');
      if (Math.abs(Date.now() - request.created) > 300000 || fs.existsSync(response)) return;
      if (uri.path === '/ping') {
        write(response, {status: 'ready', command: 'AutoTest.RunScripts'});
        return;
      }
      if (uri.path !== '/run') return;
      try {
        if (busy) throw new Error('ATS bridge already running');
        if (fs.existsSync(path.join(directory, 'ats-started.json'))) return;
        if (!Array.isArray(request.files) || !request.files.length) throw new Error('Empty test plan');
        const files = request.files.map(file => fs.realpathSync(file));
        for (const file of files) {
          if (!inside(path.join(root, 'tests_scripts'), file) ||
              !/^test_smoke_test_\d+(?:\.\d+)?(?:_row\d+)?\.py$/.test(path.basename(file))) {
            throw new Error('Test file is outside the ATS smoke plan');
          }
        }
        const extension = vscode.extensions.getExtension('ThunderSoft.AITestStudio');
        if (!extension) throw new Error('AI Test Studio is not installed');
        await extension.activate();
        const setPath = path.join(directory, 'USB_Smoke.set');
        // ATS joins entries to the workspace root; it does not accept absolute entries.
        fs.writeFileSync(setPath, '<Scripts>\n' + files.map(file =>
          `<Script isChecked="true" loop="1" name="${escapeXml(path.basename(file))}">${escapeXml(path.relative(root, file).replace(/\\/g, '/'))}</Script>`).join('\n') + '\n</Scripts>', 'utf8');
        busy = true;
        write(path.join(directory, 'ats-started.json'), {status: 'running', count: files.length});
        const setUri = vscode.Uri.file(setPath);
        const result = await vscode.commands.executeCommand('AutoTest.RunScripts', setUri, [setUri], {
          openReport: true, notify: false, reportDir: path.join(directory, 'ats-report'), deviceId: request.deviceId
        });
        write(response, {status: result && !result.aborted ? 'complete' : 'aborted', result: result || null});
      } catch (error) {
        write(response, {status: 'error', error: String(error)});
      } finally { busy = false; }
    }
  }));
}
module.exports = {activate, escapeXml, inside};
