import bpy

def get_viewport_size():
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            for r in a.regions:
                if r.type == 'WINDOW':
                    return r.width, r.height
                    #print(f"Viewport dimensions: {r.width}x{r.height}, approximate aspect rato: {round(r.width/r.height, 2)}")


"""        
def get_viewport_matrix():
    area  = [area for area in bpy.context.window.screen.areas if area.type == 'VIEW_3D'][0]
    if not area:
        raise RuntimeError("No 3D View area found.")
    with bpy.context.temp_override(area=area):
        view3d = bpy.context.space_data
        
        #Matrix
        view_matrix = view3d.region_3d.view_matrix
        perspective_matrix = view3d.region_3d.perspective_matrix
        
        #Flatten matrix representation into 1D array
        view_matrix_flatten = [item for sublist in view_matrix for item in sublist]
        perspective_matrix_flatten = [item for sublist in perspective_matrix for item in sublist]
        
        return view_matrix_flatten, perspective_matrix_flatten
"""


def get_viewport_matrix():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region = area.spaces[0].region_3d
            view_matrix = region.view_matrix
            perspective_matrix = region.perspective_matrix
            print(type(view_matrix))
            view_matrix_flatten = [item for sublist in view_matrix for item in sublist]
            perspective_matrix_flatten = [item for sublist in perspective_matrix for item in sublist]
            return view_matrix_flatten, perspective_matrix_flatten
    raise RuntimeError("No 3D View area found.")
    
    
def restore_viewport(viewport_matrix, perspective_matrix):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region = area.spaces[0].region_3d
            region.view_matrix = viewport_matrix
            #Perspective matrix is read-only
            #region.perspective_matrix = perspective_matrix