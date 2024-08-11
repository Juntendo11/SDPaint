import bpy
import os 
from PIL import Image

from math import *
from mathutils import *

from sdpaint.sd.img2img import image_gen
from sdpaint.bpy.viewport import get_viewport_size

from bpy.props import (StringProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       AddonPreferences,
                       )
# ------------------------------------------------------------------------
#    Info
# ------------------------------------------------------------------------                       
bl_info = {
    "name": "SDPaint",
    "blender": (3, 30, 0),
    "category": "Object",
}

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------


class Generate(bpy.types.Operator):
    bl_label = "Generate"
    bl_idname = "generate.myop_operator"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        my_props = scene.my_props
        prompt = mytool.pos
        negative = mytool.neg
        seed_val = my_props.seed
        denoise = my_props.denoise
        
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        outPath  = os.path.join(absolute_conf_path, "gen.png")
        print("Generating image")
        ren_img = Image.open(filepath)
        print(
        gen_img = image_gen(absolute_conf_path,ren_img,prompt,negative,seed,denoise)    #output path, img, prompt, negative
        
        #Load stencil
        import_brush(context, outPath)
        return {'FINISHED'}
    
class Render(bpy.types.Operator):
    bl_label = "Render"
    bl_idname = "render.myop_operator"

    def execute(self, context):
        scene = context.scene
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        
        width,height = get_viewport_size()
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.image_settings.file_format = "PNG"
        
        bpy.context.space_data.overlay.show_overlays = False
        bpy.ops.render.opengl(animation=False, render_keyed_only=False, sequencer=False, write_still=False, view_context=True)
        bpy.context.space_data.overlay.show_overlays = True
        
        bpy.data.images["Render Result"].save_render(filepath)
        print("Rendering image")
        return {'FINISHED'}
    
class CenterStencil(bpy.types.Operator):
    bl_label = "Center"
    bl_idname = "center.myop_operator"

    def execute(self, context):
        scene = context.scene

        #CenterStencil
        bpy.ops.brush.stencil_fit_image_aspect(use_repeat=False, use_scale=True)

        v3d_list = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D']
        if v3d_list:
            mainV3D = max(v3d_list, key=lambda area: area.width * area.height)
               
            x = mainV3D.width / 2
            y = mainV3D.height / 2
            
            try:
                if bpy.context.sculpt_object:   
                    brushName = bpy.context.tool_settings.sculpt.brush.name
                else:
                    brushName = bpy.context.tool_settings.image_paint.brush.name
                    
                bpy.data.brushes[brushName].stencil_pos.xy = x, y
                width,height = get_viewport_size()
                bpy.data.brushes[brushName].stencil_dimension.xy = width/2,height/2
                
            except:
                pass

        return {'FINISHED'}
    
class StencilOpacity(bpy.types.Operator):
    bl_label = "Opacity"
    bl_idname = "opacity.myop_operator"
    opacity: bpy.props.FloatProperty(name="Opacity",description="Opacity",default=0.1, min=0.0, max=1.0)

    def execute(self, context):
        scene = context.scene
        my_props = scene.my_props
        opacity_val=my_props.opacity
        setting = self.setting
        brush = bpy.context.tool_settings.image_paint.brush
        
        brush = bpy.data.brushes[brush_name]
        brush.texture_slot.opacity = opacity_val
        print(opacity_val)




# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

    api: StringProperty(
        name="API Key",
        description=":",
        default="",
        maxlen=1024,
        )
    pos: StringProperty(
        name="Prompt",
        description=":",
        default="",
        maxlen=1024,
        )
    neg: StringProperty(
        name="Negative",
        description=":",
        default="",
        maxlen=1024,
        )

    seed: bpy.props.IntProperty(
        name="seed",
        description="Seed value",
        default=-1,
    )
    
    denoise: bpy.props.FloatProperty(
        name="denoise",
        description="Denoising scale",
        default=0.5,
        min=0.0,
        max=1.0
    )

    opacity: bpy.props.FloatProperty(
        name="opacity",
        description="Stencil opacity",
        default=0.5,
        min=0.0,
        max=1.0
    )


# ------------------------------------------------------------------------
#    Panel in TexPaint Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "SD_Paint"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "SDPaint"
    bl_context = "imagepaint"

    
    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        my_props = scene.my_props

        layout.prop(mytool, "api")
        layout.prop(mytool, "pos")
        layout.prop(mytool, "neg")
        layout.prop(my_props,"seed")
        layout.prop(my_props,"denoise")
        
        layout.separator()
        
        col = layout.column()
        col.prop(context.scene, 'conf_path')

        layout.separator()

        layout.operator("generate.myop_operator")
        layout.operator("render.myop_operator")
        layout.operator("center.myop_operator")
        layout.prop(my_props,"opacity")

        
# ------------------------------------------------------------------------
#    Functions
# ------------------------------------------------------------------------

def import_brush(context, filepath):
    
    file = os.path.split(filepath)[-1]

    if os.path.isfile(filepath):
        brush = bpy.data.brushes.new(file,mode='TEXTURE_PAINT')
        tex   = bpy.data.textures.new(file,type="IMAGE")
        image = bpy.data.images.load(filepath, check_existing=False)
        tex.image = image
        
        #Set as texture 
        brush.texture = tex
        brush.texture_slot.map_mode = 'STENCIL'

        #Disable
        """
        brush.use_custom_icon = True
        brush.icon_filepath = filepath
        brush.strength = options.default_strength
        brush.blend = options.blend
        """
        #brush.texture_slot.scale =  Vector((brush.texture_slot.scale.x*(2), brush.texture_slot.scale.y*(2), 1.0))

    return {'FINISHED'}

    
# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    OBJECT_PT_CustomPanel,
    Generate,
    Render,
    CenterStencil,
    StencilOpacity,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties)

    #Directory path
    bpy.types.Scene.conf_path = bpy.props.StringProperty \
      (
      name = "Output Path",
      default = "",
      description = "Define the root path of the project",
      subtype = 'DIR_PATH',
      )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.conf_path


if __name__ == "__main__":
    register()