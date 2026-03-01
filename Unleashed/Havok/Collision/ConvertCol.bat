for %%f in (*.phy.hkx) do col2fbx %%f
for %%f in (*.fbx) do fbx2col %%f
del *.fbx