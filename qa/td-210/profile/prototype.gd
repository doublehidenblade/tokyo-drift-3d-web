extends SceneTree
const Shared = preload("res://scripts/lower_city/city_kit_instances.gd")
const HALL := "res://assets/td-186/buildings/kamome_hall/kamome_hall.glb"
func _initialize() -> void:
	run.call_deferred()
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var shared := args[0] == "shared"
	var kit = Shared.new() if shared else CityKitBatch.new()
	var holder := Node3D.new()
	root.add_child(holder)
	var initial := OS.get_static_memory_usage()
	var start := Time.get_ticks_usec()
	var surfaces: Array = kit.source(HALL)
	var loaded := Time.get_ticks_usec()
	for i in 24:
		var xf := Transform3D(Basis(Vector3.UP,float(i%4)*PI/2.0), Vector3((i%8)*36.0,0,(i/8)*36.0))
		if shared:
			kit.place_shared("hall","prototype",surfaces,xf,Color.WHITE,420,1022+i,"hall")
		else:
			kit.place("prototype",surfaces,xf,Color.WHITE,420,1022+i,"hall")
	var placed := Time.get_ticks_usec()
	var nodes: Array = kit.flush(holder)
	var flushed := Time.get_ticks_usec()
	var retained := OS.get_static_memory_usage()
	var records: Array[String] = []
	var unique := {}
	var mats := {}
	var max_bounds := Vector3.ZERO
	for node in nodes:
		var mesh: Mesh = node.multimesh.mesh if node is MultiMeshInstance3D else node.mesh
		unique[mesh] = true
		var count: int = node.multimesh.instance_count if node is MultiMeshInstance3D else 1
		var bound: AABB = node.multimesh.custom_aabb if node is MultiMeshInstance3D else mesh.get_aabb()
		max_bounds = max_bounds.max(bound.size)
		for inst in count:
			var xf: Transform3D = node.transform * (node.multimesh.get_instance_transform(inst) if node is MultiMeshInstance3D else Transform3D.IDENTITY)
			for si in mesh.get_surface_count():
				var arr: Array = mesh.surface_get_arrays(si)
				var mat: Material = mesh.surface_get_material(si)
				mats[mat] = true
				var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
				var pts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
				if idx.is_empty():
					for k in pts.size(): idx.append(k)
				for k in idx:
					var p: Vector3 = xf*pts[k]
					var n: Vector3 = (xf.basis*arr[Mesh.ARRAY_NORMAL][k]).normalized()
					var uv: Vector2 = arr[Mesh.ARRAY_TEX_UV][k]
					var col: Color = arr[Mesh.ARRAY_COLOR][k]
					records.append(str([roundi(p.x*1000),roundi(p.y*1000),roundi(p.z*1000),roundi(n.x*1000),roundi(n.y*1000),roundi(n.z*1000),roundi(uv.x*10000),roundi(uv.y*10000),col.to_html(),mat.resource_name]))
	records.sort()
	FileAccess.open("/tmp/td210-"+args[0]+"-vertices.json",FileAccess.WRITE).store_string(JSON.stringify(records))
	var stored := 0
	for mesh: Mesh in unique:
		for si in mesh.get_surface_count():
			stored += var_to_bytes(mesh.surface_get_arrays(si)).size()
	var result := {"mode":args[0],"placements":24,"expanded_triangles":records.size()/3,"equivalence_sha256":"\n".join(records).sha256_text(),"unique_meshes":unique.size(),"unique_materials":mats.size(),"geometry_array_bytes":stored,"initial_bytes":initial,"retained_bytes":retained,"delta_bytes":retained-initial,"peak_bytes":OS.get_static_memory_peak_usage(),"source_load_us":loaded-start,"placement_us":placed-loaded,"flush_us":flushed-placed,"total_us":flushed-start,"batch_nodes":nodes.size(),"max_bounds_m":str(max_bounds),"timings":kit.timings}
	FileAccess.open(args[1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print(JSON.stringify(result))
	holder.free()
	quit()
