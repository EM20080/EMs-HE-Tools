for %%f in (source\*.hkx) do AssetCcGens.exe -x "%%f" "output\%%~nf.xml"
for %%f in (output\*.xml) do (python ..\Havok.py "%%f" "output\%%~nf_550.xml" & if exist "output\%%~nf_550.xml" (del "%%f" & ren "output\%%~nf_550.xml" "%%~nf.xml"))
for %%f in (output\*.xml) do (AssetCcUnleashed.exe --rules4001 "%%f" "output\%%~nf.hkx" 2>nul & del "%%f")