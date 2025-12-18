bl_info = {
    "name": "HE1 Shapekey Importer",
    "author": "EM",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "File > Import"
}

import bpy
import xml.etree.ElementTree as ET
from bpy_extras.io_utils import ImportHelper


def _mesh(ctx):
    o = ctx.active_object
    if o and o.type == "MESH":
        return o
    for obj in ctx.selected_objects:
        if obj.type == "MESH":
            return obj
    return None


def _read_xml(path):
    root = ET.parse(path).getroot()
    anim = root.find("Animation")
    if anim is None:
        anim = root.find(".//Animation")
    if anim is None:
        return None, [], 1.0, None, None, None, None

    sets = []
    max_abs = 0.0
    min_f = None
    max_f = None

    for ks in anim.findall("KeyframeSet"):
        name = ks.get("name") or ""
        if not name:
            continue
        frames = []
        for kf in ks.findall("Keyframe"):
            idx = kf.get("index") or kf.get("frame") or kf.get("t")
            val = kf.get("value")
            if idx is None or val is None:
                continue
            try:
                f = float(idx)
                v = float(val)
            except Exception:
                continue
            frames.append((f, v))
            av = abs(v)
            if av > max_abs:
                max_abs = av
            if min_f is None or f < min_f:
                min_f = f
            if max_f is None or f > max_f:
                max_f = f
        if frames:
            sets.append((name, frames))

    scale = 0.01 if max_abs > 2.0 else 1.0

    sf = anim.get("start_frame")
    ef = anim.get("end_frame")

    return anim, sets, scale, min_f, max_f, sf, ef


def _lookup(sk):
    d = {}
    for kb in sk.key_blocks:
        n = kb.name
        d[n] = kb
        d[n.lower()] = kb
        base = n.split(".")[0]
        d[base] = kb
        d[base.lower()] = kb
    return d


class ImportShapekeyXML(bpy.types.Operator, ImportHelper):
    bl_idname = "import.shapekey_xml"
    bl_label = "import shapekey (.xml)"
    filename_ext = ".xml"

    def execute(self, ctx):
        o = _mesh(ctx)
        if not o:
            return {'CANCELLED'}

        try:
            anim, sets, scale, min_f, max_f, sf, ef = _read_xml(self.filepath)
        except Exception:
            return {'CANCELLED'}

        if anim is None or not sets:
            return {'CANCELLED'}

        if o.data.shape_keys is None:
            o.shape_key_add(name="Basis", from_mix=False)

        sk = o.data.shape_keys
        if sk.animation_data is None:
            sk.animation_data_create()

        act = bpy.data.actions.new(name="MorphWeight")
        sk.animation_data.action = act

        lk = _lookup(sk)

        first_nonzero = None
        keyed = 0
        eps = 1e-6

        for name, frames_vals in sets:
            kb = lk.get(name) or lk.get(name.lower())
            if kb is None:
                continue

            try:
                sk.key_blocks.active_index = sk.key_blocks.find(kb.name)
            except Exception:
                pass

            for f, raw_v in frames_vals:
                v = raw_v * scale
                if first_nonzero is None and abs(v) > eps:
                    first_nonzero = int(f)
                kb.value = v
                kb.keyframe_insert(data_path="value", frame=f, group=kb.name)
                keyed += 1

        try:
            ctx.view_layer.update()
        except Exception:
            pass

        s = ctx.scene
        if sf is None and min_f is not None:
            sf = min_f
        if ef is None and max_f is not None:
            ef = max_f
        try:
            if sf is not None:
                s.frame_start = int(float(sf))
            if ef is not None:
                s.frame_end = int(float(ef))
        except Exception:
            pass

        if first_nonzero is not None:
            try:
                s.frame_set(first_nonzero)
            except Exception:
                pass

        return {'FINISHED'} if keyed else {'CANCELLED'}


def menu_func_import(self, ctx):
    self.layout.operator(ImportShapekeyXML.bl_idname, text="import shapekey (.xml)")


def register():
    bpy.utils.register_class(ImportShapekeyXML)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ImportShapekeyXML)
