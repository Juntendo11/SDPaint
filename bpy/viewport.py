import bpy

def get_viewport_size():
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            for r in a.regions:
                if r.type == 'WINDOW':
                    return r.width, r.height
                    #print(f"Viewport dimensions: {r.width}x{r.height}, approximate aspect rato: {round(r.width/r.height, 2)}")
                    
