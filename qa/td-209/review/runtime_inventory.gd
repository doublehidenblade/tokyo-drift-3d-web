extends SceneTree
## Validator-only inventory of ordinary production construction (QA retention remains off).

func _initialize() -> void:
	run.call_deferred()

func run() -> void:
	var world := LowerCityWorld.new()
	root.add_child(world)
	if not world.is_built:
		await world.build_completed
	var kit := world.tenjin_buildings.kit
	var materials := {}
	var nodes: Array = []
	var total_triangles := 0
	var total_surfaces := 0
	var unsafe: Array = []
	for node: MeshInstance3D in world.tenjin_buildings.nodes:
		var tris := 0
		for si in node.mesh.get_surface_count():
			var arrays := node.mesh.surface_get_arrays(si)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			tris += (indices.size() if not indices.is_empty() else vertices.size()) / 3
			var material: StandardMaterial3D = node.get_active_material(si)
			var id := str(material.get_instance_id())
			if not materials.has(id):
				materials[id] = {"name": material.resource_name, "surface_uses": 0,
					"albedo": material.albedo_texture.resource_path if material.albedo_texture else "",
					"emission": material.emission_texture.resource_path if material.emission_texture else "",
					"opaque": material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED,
					"cull_back": material.cull_mode == BaseMaterial3D.CULL_BACK,
					"next_pass_null": material.next_pass == null}
			materials[id].surface_uses += 1
			if not materials[id].opaque or not materials[id].cull_back or not materials[id].next_pass_null:
				unsafe.append([node.name, si])
		var bounds := node.get_aabb()
		nodes.append({"name": str(node.name), "family": node.get_meta("kit_family"),
			"surfaces": node.mesh.get_surface_count(), "triangles": tris,
			"bounds_size": [bounds.size.x,bounds.size.y,bounds.size.z],
			"visibility_end": node.visibility_range_end, "visibility_margin": node.visibility_range_end_margin,
			"baked_ink": node.get_meta("anime_baked_ink", false), "children": node.get_child_count()})
		total_triangles += tris
		total_surfaces += node.mesh.get_surface_count()
	var result := {"source_runtime": "6f7818b45cd09ade3ca621354ce4eb116050a66b",
		"engine": Engine.get_version_info(), "ordinary_retain_placement_flag": CityKitBatch.retain_placement_evidence,
		"retained_placement_records": kit.placements.size(),
		"construction_caches": {"assets":kit.assets.size(),"donors":kit.donors.size(),"modules":kit.modules.size(),"batches":kit.batches.size()},
		"mesh_count": nodes.size(), "surface_count": total_surfaces, "triangles_from_mesh_arrays": total_triangles,
		"unique_material_resources": materials.size(), "materials": materials.values(), "nodes": nodes,
		"unsafe_materials": unsafe, "world_stats": world.stats}
	FileAccess.open(OS.get_cmdline_user_args()[0], FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TD209_REVIEW_INVENTORY meshes=",nodes.size()," surfaces=",total_surfaces," materials=",materials.size()," triangles=",total_triangles," retained_placements=",kit.placements.size()," unsafe=",unsafe.size())
	world.free()
	quit(0 if unsafe.is_empty() and total_triangles == 758474 and kit.placements.is_empty() else 1)
