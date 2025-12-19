for %%a in ("*.anm.hkx") do for %%m in ("*.model") do modelfbx "%%m" "%%~dpnm.skl.hkx" "%%a" "%%~dpna.fbx"
pause