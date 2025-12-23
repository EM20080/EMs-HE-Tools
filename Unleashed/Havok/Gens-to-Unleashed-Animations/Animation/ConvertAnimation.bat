for %%f in (source\*.hkx) do AssetCcGens.exe -x "%%f" "output\%%~nxf.xml"
for %%f in (output\*.xml) do gens2unleashed-animconverter.exe "%%f" "%%f"
for %%f in (output\*.xml) do (AssetCcUnleashed.exe --rules4001 "%%f" "%%~dpnf" 2>nul & del "%%f")