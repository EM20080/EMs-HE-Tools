for %%f in (source\*.hkx) do Havok "%%f" "output\%%~nf.xml"
for %%f in (output\*.xml) do (AssetCcUnleashed.exe --rules4001 "%%f" "%%~dpnf.hkx" 2>nul & del "%%f")