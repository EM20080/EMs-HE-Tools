for %%f in (source\*.skl.hkx) do modelfbx "%%f" "output\%%~nf.fbx"
for %%f in (output\*.fbx) do HavokAnimationExporter-550.exe "%%f"
del /q output\*.fbx
pause