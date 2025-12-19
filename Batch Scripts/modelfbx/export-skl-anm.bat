for %%f in (*.fbx) do HavokAnimationExporter-550 %%f
for %%f in (*.fbx) do HavokAnimationExporter-550 "%%f" --skl "%%~nf.skl.hkx" -u -f 60 %1