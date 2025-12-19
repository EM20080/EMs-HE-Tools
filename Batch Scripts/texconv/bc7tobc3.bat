texconv *.dds -ft png -f R8G8B8A8_UNORM
del *.dds
texconv *.png -f BC3_UNORM -ft dds -bc d -y
del *.png