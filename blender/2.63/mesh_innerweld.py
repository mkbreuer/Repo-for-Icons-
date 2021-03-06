# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__bpydoc__ = """\
InnerWeld.  This addon welds parallel connected selected edges together. 

Documentation

First go to User Preferences->Addons and enable the InnerWeld addon in the Mesh category.
Go to EditMode, select some parallel edge(loop)(slices).  Handles ALL edges parallel next to each other.
These edges will be welded together when invoking addon (button in Mesh Tools panel).

If you wish to hotkey InnerWeld:
In the Input section of User Preferences at the bottom of the 3D View > Mesh section click 'Add New' button.
In the Operator Identifier box put 'mesh.innerweld'.
Assign a hotkey.
Save as Default (Optional).
"""


bl_info = {
	"name": "InnerWeld",
	"author": "Gert De Roost",
	"version": (0, 1, 0),
	"blender": (2, 6, 3),
	"location": "View3D > Tools",
	"description": "Welding parallel edges together.",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}

if "bpy" in locals():
    import imp


import bpy
import bmesh




class InnerWeld(bpy.types.Operator):
	bl_idname = "mesh.innerweld"
	bl_label = "InnerWeld"
	bl_description = "Welding parallel edges together"
	bl_options = {"REGISTER", "UNDO"}

	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

	def invoke(self, context, event):
		
		self.save_global_undo = bpy.context.user_preferences.edit.use_global_undo
		bpy.context.user_preferences.edit.use_global_undo = False
		
		do_innerweld()
		
		bpy.context.user_preferences.edit.use_global_undo = self.save_global_undo
		bm.free()
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()
		
		return {'FINISHED'}


def panel_func(self, context):
	
	scn = bpy.context.scene
	self.layout.label(text="InnerWeld:")
	self.layout.operator("mesh.innerweld", text="Weld Edges")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_PT_tools_meshedit.append(panel_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_PT_tools_meshedit.remove(panel_func)

if __name__ == "__main__":
	register()





def addstart(vert):
	
	global sellist, vertlist

	# recursive: adds to initial edgelist at start
	for e in vert.link_edges:
		if e in sellist:
			sellist.pop(sellist.index(e))
			v = e.other_vert(vert)
			vertlist[posn].insert(0, v)
			addstart(v)

def addend(vert):
	
	global sellist, vertlist

	# recursive: adds to initial edgelist at end
	for e in vert.link_edges:
		if e in sellist:
			sellist.pop(sellist.index(e))
			v = e.other_vert(vert)
			vertlist[posn].append(v)
			addend(v)


def do_innerweld():

	global sellist, vertlist, posn
	global bm

	context = bpy.context
	region = context.region  
	area = context.area
	selobj = bpy.context.active_object
	mesh = selobj.data
	bm = bmesh.from_edit_mesh(mesh)

	sellist = []
	for edge in bm.edges:
		if edge.select:
			sellist.append(edge)

	posn = 0
	vertlist = []
	while len(sellist) > 0:
		# initialize next edgesnake		
		vertlist.append([])
		vert = sellist[0].verts[0]
		vertlist[posn].append(vert)
		# add to start and end of arbitrary start vert
		addstart(vert)
		addend(vert)
		posn += 1
		
	found = 1	
	posn = 0
	mergesets = []
	while found:
		found = 0
		for idx in range(len(vertlist)):
			if len(vertlist[idx]) > 0:
				found = 1
				vset = set([])
				vset.add(vertlist[idx].pop())
				mergesets.append(vset.copy())
				while len(vset) > 0:
					vert = vset.pop()
					for edge in vert.link_edges:
						if edge.select:
							continue
						v1 = edge.other_vert(vert)
						for vlist in vertlist:
							if v1 in vlist and not(v1 in mergesets[posn]):
								mergesets[posn].add(v1)
								vset.add(v1)
								vertlist[vertlist.index(vlist)].pop(vlist.index(v1))
				posn +=1

	for st in mergesets:
		bpy.ops.mesh.select_all(action="DESELECT")
		for vert in st:
			vert.select = 1
		bpy.ops.mesh.merge(type='CENTER', uvs=True)
	
	
	
	
