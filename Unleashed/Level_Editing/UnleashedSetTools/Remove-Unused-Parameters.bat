for %%f in ("source/*.xml") do SetCleaner source/%%f output/%%f
del /S /Q *.bak