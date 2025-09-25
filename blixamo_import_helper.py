# BLIXAMO IMPORT HELPER
# Makes it faster and easier to import Mixamo animations into Blender.
#
# VERSION HISTORY:
# 1.0.0
# Implemented "Model" and "Animations" buttons. They indirectly utilize the
# ImportFbxFiles Operator to import FBX files and keep or delete armatures.
# They also rename imported animations to the names of their source FBX files.

import bpy
import os
from bpy.types import Operator
from bpy.props import BoolProperty
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


bl_info = {
    "name": "Blixamo",
    "author": "bdog",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Blixamo",
    "warning": "",
    "description": "Makes it faster and easier to import Mixamo animations into Blender.",
    "wiki_url": "",
    "doc_url": "",
    "category": "Import-Export",
}


class BlixamoPanel(bpy.types.Panel):
    """Creates a Blixamo panel in the 3D Viewport Sidebar"""
    bl_label = "Blixamo Import Helper" # Panel header label
    bl_idname = "BLIXAMO_PT_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blixamo" # Panel tab name

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.scale_y = 0.7  # Shrink vertical row spacing
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Import FBX:")

        row = layout.row()
        row.operator("custom.select_fbx_keep_armature")
        row = layout.row()
        row.operator("custom.select_fbx")
        

class ImportFbxKeepArmature(Operator):
    """Imports FBX file(s) and keeps armature(s)""" # bl_description docstring
    bl_idname = "custom.select_fbx_keep_armature"
    bl_label = "Model"
    
    def execute(self, context):
        bpy.ops.custom.select_files('INVOKE_DEFAULT')
        return {'FINISHED'}
        

class ImportFbxDeleteArmature(Operator):
    """Imports FBX file(s) and deletes armature(s)""" # bl_description docstring
    bl_idname = "custom.select_fbx"
    bl_label = "Animation(s)"
    
    def execute(self, context):
        bpy.ops.custom.select_files('INVOKE_DEFAULT', keep_armature=False)
        return {'FINISHED'}
        

class ImportFbxFiles(Operator, ImportHelper):
    """Imports FBX file(s) and handles armature(s)""" # bl_description docstring
    bl_idname = "custom.select_files"
    bl_label = "Select FBX Files"

    # Indicate whether to keep or delete armature
    keep_armature: BoolProperty(
        name="Keep Armature",
        options={'HIDDEN'},
        description="If True, keep armature; if False, delete armature",
        default=True
    )
    
    # Show only FBX files in file browser
    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    # Allow multiple file selection
    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    
    def execute(self, context):
        dir = os.path.dirname(self.filepath)
        
        for file in self.files:
            if file.name.lower().endswith('.fbx'):
                fbx_file_path = os.path.join(dir, file.name)
                prev_armatures = {obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'}
                prev_actions = set(bpy.data.actions)

                # Import FBX file
                bpy.ops.import_scene.fbx(filepath=fbx_file_path)

                # Get file name without extension
                file_name = os.path.splitext(os.path.basename(fbx_file_path))[0]

                # Find newly imported action by comparing with previously existing actions
                new_actions = set(bpy.data.actions) - prev_actions

                # Rename the new action
                for action in new_actions:
                    action.name = file_name
                    break # Stop renaming after the 1st action

                # Get the new armature
                new_armature = None
                for obj in bpy.context.scene.objects:
                    if obj.type == 'ARMATURE' and obj not in prev_armatures:
                        new_armature = obj
                        break

                # Delete the armature
                if new_armature and not self.keep_armature:
                    # Select only the imported armature
                    bpy.ops.object.select_all(action='DESELECT')
                    new_armature.select_set(True)
                    bpy.context.view_layer.objects.active = new_armature
                    
                    # Delete the imported armature
                    bpy.ops.object.delete()
                    
                    # Print list of preserved animations
                    for obj in bpy.context.scene.objects:
                        if obj.animation_data:
                            print(f"Preserved animation: {obj.name}")
                elif not new_armature:
                    print("Armature not found in FBX file.")
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ImportFbxFiles)
    bpy.utils.register_class(BlixamoPanel)
    bpy.utils.register_class(ImportFbxKeepArmature)
    bpy.utils.register_class(ImportFbxDeleteArmature)


def unregister():
    bpy.utils.unregister_class(ImportFbxDeleteArmature)
    bpy.utils.unregister_class(ImportFbxKeepArmature)
    bpy.utils.unregister_class(ImportFbxFiles)
    bpy.utils.unregister_class(BlixamoPanel)


if __name__ == "__main__":
    register()
#    unregister()
