import bpy
import mathutils
from mathutils import Vector
import bmesh
from bpy import context
import numpy as np

def triangulate_object(obj):
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.new()
    bm.from_mesh(me)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()
    return me


def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True


    scn = bpy.context.scene
    scn.collection.objects.link(ob)

    bpy.context.view_layer.objects.active=ob
    ob.select_set(True)
    #scn.collection.objects.link(ob)
    #scn.collection.objects.active = ob



    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me=triangulate_object(ob)
    me.update()
    return ob

def makeFaces(verts):
    faces=[]
    #100x100 points since each bezier curve has 100 points
    length_curve = int(1/.01)

    for i in range(length_curve - 1):
        for j in range(length_curve - 1):
            index = []
            index.append(i*length_curve + j)
            index.append((i+1)*length_curve+j)
            index.append((i+1)*length_curve+j+1)
            index.append(i*length_curve+j+1)
            faces.append(index)
    return faces

def readVertices(fileName):
    vertices=[]
    for line in open(fileName,"r"):
        if line.startswith('#'):continue
        values=line.split()
        if not values:continue
        if values[0]=='v':
            vertex=[]
            vertex.append(float(values[1]))
            vertex.append(float(values[2]))
            vertex.append(float(values[3]))
            vertices.append(vertex)
    return vertices

def readSplit(fileName):
    for line in open(fileName,"r"):
        if line.startswith('#'):continue
        values=line.split()
        if not values:continue
        if values[0]!='v':
            sp=int(values[0])
    return sp

#Computes Bezier curve through De casteljau algorithm
def decajau(cPoly,t):
    nrCPs = cPoly.shape[0]
    # P = (CPs, coordinates, levels)
    P = np.zeros((nrCPs, 2, nrCPs))
    P[:,:,0] = cPoly;
    for i in range(0,nrCPs):
        for j in range(0, nrCPs-(i+1)):

            P[j,:,i+1] = (1-t)*P[j,:,i] + t*P[j+1,:,i]

    point = P[0,:,nrCPs-1];
    return point

#Compute vertices on coons patch
def coon(curve, curve2, curve3, curve4, steps):
    patch1, patch2, patch3 = [], [], []

    #Set boundary points
    p1 = curve[0]
    p2 = curve[-1]
    p3 = curve2[0]
    p4 = curve2[-1]

    for u in range(int(1/steps)):
        for v in range(int(1/steps)):
            patch1_point= (1-u*steps)*curve[u,:]+u*steps*curve2[u,:]
            patch1.append(patch1_point)
            patch2_point = (1-v*steps)*curve3[v,:]+v*steps*curve4[v,:]
            patch2.append(patch2_point)
            patch3_point = (1-u*steps)*(1-v*steps)*p1+u*steps*(1-v*steps)*p2+v*steps*(1-u*steps)*p3+u*steps*v*steps*p4
            patch3.append(patch3_point)

    coons_patch = np.array(patch1)+np.array(patch2)-np.array(patch3)

    return coons_patch


def export_obj(filepath,obj):
    mesh = obj.data
    with open(filepath, 'w') as f:
        f.write("# OBJ file\n")
        for v in mesh.vertices:
            f.write("v %.4f %.4f %.4f\n" % v.co[:])
        for p in mesh.polygons:
            f.write("f")
            for i in p.vertices:
                f.write(" %d" % (i + 1))
            f.write("\n")

def make_ob_file(verts):
    faces=makeFaces(verts)
    ob=createMeshFromData("test",(0,0,0),verts,faces)
    return ob

def make_Verts(file_path):
    verts=readVertices(file_path)
    return verts

#Parameter step size for bezier curve
step = .01

#compute bezier curve 1
file_path="C:\\Users\\sushr\\oneDrive\\Desktop\\CMPT 732\\Assignment2\\blender\\blenderScripts\\cpoints1.txt"
points = np.array(make_Verts(file_path))
curve = np.zeros((round(1/step),3))
for i in np.arange(0.0,1.0,step):
    curve[round(i*(1/step)),(0,2)]=decajau(points[:,(0,2)],i)

#compute bezier curve 2
file_path="C:\\Users\\sushr\\oneDrive\\Desktop\\CMPT 732\\Assignment2\\blender\\blenderScripts\\cpoints2.txt"
points2 = np.array(make_Verts(file_path))
curve2 = np.zeros((round(1/step),3))
for i in np.arange(0.0,1.0,step):
    curve2[round(i*(1/step)),(0,2)]=decajau(points2[:,(0,2)],i)

#plane y = 3
curve2[:,1] = 3

#compute bezier curve 3
file_path="C:\\Users\\sushr\\oneDrive\\Desktop\\CMPT 732\\Assignment2\\blender\\blenderScripts\\cpoints3.txt"
points3 = np.array(make_Verts(file_path))
curve3 = np.zeros((round(1/step),3))
for i in np.arange(0.0,1.0,step):
    curve3[round(i*(1/step)),(1,2)]=decajau(points3[:,(1,2)],i)

#compute bezier curve 4
file_path="C:\\Users\\sushr\\oneDrive\\Desktop\\CMPT 732\\Assignment2\\blender\\blenderScripts\\cpoints4.txt"
points4 = np.array(make_Verts(file_path))
curve4 = np.zeros((round(1/step),3))
for i in np.arange(0.0,1.0,step):
    curve4[round(i*(1/step)),(1,2)]=decajau(points4[:,(1,2)],i)

#plane x = 6
curve4[:,0]=6

#compute coons patch
patch = coon(curve, curve2, curve3, curve4, step)
objects = make_ob_file(patch)

filepath = "C:\\Users\\sushr\\oneDrive\\Desktop\\CMPT 732\\Assignment2\\blender\\blenderScripts\\test.obj"
obj = context.object
export_obj(filepath,obj)
