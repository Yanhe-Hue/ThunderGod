"""Package the small local VS Code connector without external build dependencies."""
from pathlib import Path
import zipfile

root = Path(__file__).parent
target = root / 'ats_bridge' / 'usbupdate-ats-bridge-1.0.2.vsix'
manifest = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
<Metadata><Identity Language="en-US" Id="usbupdate-ats-bridge" Version="1.0.2" Publisher="local-usbupdate"/>
<DisplayName>USB Upgrade ATS Bridge</DisplayName><Description xml:space="preserve">Connect USB upgrade automation to ATS execution.</Description>
<Properties><Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.75.0"/></Properties></Metadata>
<Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/>
<Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/></Assets>
</PackageManifest>'''
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('extension.vsixmanifest', manifest)
    archive.writestr('[Content_Types].xml', '''<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="json" ContentType="application/json"/><Default Extension="js" ContentType="application/javascript"/><Default Extension="vsixmanifest" ContentType="text/xml"/></Types>''')
    for name in ('package.json', 'extension.js'):
        archive.write(root / 'ats_bridge' / name, 'extension/' + name)
print(target)
