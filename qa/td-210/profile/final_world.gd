extends SceneTree
## Quiet, fresh-process construction; existing progress signals give phase boundaries.
## Headless static memory excludes GPU allocation. No device frame-rate claim.
var stages: Array = []
var previous_us := 0
func _initialize() -> void:
	run.call_deferred()
func progress(_fraction: float, stage: String) -> void:
	var now := Time.get_ticks_usec()
	stages.append({"stage":stage,"duration_us":now-previous_us,"static_bytes":OS.get_static_memory_usage()})
	previous_us=now
func run() -> void:
	seed(185)
	var world:=LowerCityWorld.new()
	world.build_progress.connect(progress)
	previous_us=Time.get_ticks_usec()
	root.add_child(world)
	if not world.is_built: await world.build_completed
	var result:={"world_stats":world.stats,"stages":stages,"static_memory_bytes":OS.get_static_memory_usage(),"static_memory_peak_bytes":OS.get_static_memory_peak_usage(),"engine":Engine.get_version_info(),"seed":185}
	var materials:={}
	var meshes:={}
	var families:={}
	for family in world.meshes:
		var count:=0
		for node in world.meshes[family]:
			var mesh:Mesh=node.multimesh.mesh if node is MultiMeshInstance3D else node.mesh
			meshes[mesh]=true
			for si in mesh.get_surface_count():
				var mat:Material=node.material_override if node.material_override!=null else mesh.surface_get_material(si)
				materials[mat]=true
			count+=1
		families[family]=count
	result.geometry_nodes_by_family=families
	result.unique_mesh_resources=meshes.size()
	result.unique_material_resources=materials.size()
	var look:=AnimeLook.new()
	look.palette=load("res://data/anime/trench.tres")
	var start:=Time.get_ticks_usec()
	look._toon_tree(world,[])
	result.material_conversion_us=Time.get_ticks_usec()-start
	result.after_material_conversion_static_bytes=OS.get_static_memory_usage()
	result.after_material_conversion_peak_bytes=OS.get_static_memory_peak_usage()
	var shaders:={}
	for family in world.meshes:
		for node in world.meshes[family]:
			var mesh:Mesh=node.multimesh.mesh if node is MultiMeshInstance3D else node.mesh
			for si in mesh.get_surface_count():
				var mat:Material=node.material_override if node.material_override!=null else mesh.surface_get_material(si)
				shaders[mat]=true
	result.unique_mesh_surface_materials_after_conversion=shaders.size()
	FileAccess.open(OS.get_cmdline_user_args()[0],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	look.free();world.free();quit()
