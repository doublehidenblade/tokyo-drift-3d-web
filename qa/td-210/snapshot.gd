extends SceneTree
## Exact protected world-geometry snapshot. This same file runs in the pinned base and final tree.
var lot_bounds: Array = []

func in_kamome(p: Vector2, lots: Array) -> bool:
	for i in lots.size():
		if not (lot_bounds[i] as Rect2).has_point(p):
			continue
		var poly: PackedVector2Array = lots[i]
		if Geometry2D.is_point_in_polygon(p,poly):
			return true
		for k in poly.size():
			if p.distance_to(Geometry2D.get_closest_point_to_segment(p,poly[k],poly[(k+1)%poly.size()])) < 2.9:
				return true
	return false
func _initialize() -> void:
	run.call_deferred()

func run() -> void:
	var world := LowerCityWorld.new()
	root.add_child(world)
	if not world.is_built:
		await world.build_completed
	await process_frame
	var lots: Array = []
	for lot: Dictionary in world.data.lots:
		if lot.d == "kamome":
			var poly := PackedVector2Array()
			for q in lot.p:
				poly.append(Vector2(q[0],q[1]))
			lots.append(poly)
			var bounds := Rect2(poly[0],Vector2.ZERO)
			for p in poly:
				bounds = bounds.expand(p)
			lot_bounds.append(bounds.grow(2.9))
	var retained := PackedVector3Array()
	var wall_shape: ConcavePolygonShape3D = world.walls.get_child(0).shape
	var walls := wall_shape.get_faces()
	for k in range(0,walls.size(),3):
		var p := CityData.plan((walls[k]+walls[k+1]+walls[k+2])/3.0)
		if not in_kamome(p,lots):
			retained.append_array(walls.slice(k,k+3))
	var drive: ConcavePolygonShape3D = world.drivable.get_child(0).shape
	var result := {"engine": Engine.get_version_info(), "world_stats": world.stats,
		"drive_sha256": drive.get_faces().to_byte_array().hex_encode().sha256_text(),
		"walls_outside_kamome_sha256": retained.to_byte_array().hex_encode().sha256_text(),
		"walls_outside_kamome_triangles": retained.size()/3, "protected_meshes": {}, "tenjin_meshes": []}
	for family: String in world.meshes:
		if family == "kamome": continue
		if family in ["bldg","metal","lamps"]:
			var protected := PackedFloat32Array()
			var canonical: Array[String] = []
			for node: MeshInstance3D in world.meshes[family]:
				for si in node.mesh.get_surface_count():
					var arr := node.mesh.surface_get_arrays(si)
					var vertices: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
					var indices: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
					for k in range(0,indices.size(),3):
						var center: Vector3 = (vertices[indices[k]]+vertices[indices[k+1]]+vertices[indices[k+2]])/3.0+node.position
						if in_kamome(CityData.plan(center),lots):
							continue
						for j in 3:
							var ix := indices[k+j]
							var p: Vector3 = vertices[ix]+node.position
							var n: Vector3 = arr[Mesh.ARRAY_NORMAL][ix]
							var uv: Vector2 = arr[Mesh.ARRAY_TEX_UV][ix]
							var c: Color = arr[Mesh.ARRAY_COLOR][ix]
							protected.append_array([p.x,p.y,p.z,n.x,n.y,n.z,uv.x,uv.y,c.r,c.g,c.b,c.a])
			for offset in range(0,protected.size(),36):
				canonical.append(protected.slice(offset,offset+36).to_byte_array().hex_encode().sha256_text())
			canonical.sort()
			result[family+"_canonical_sha256"] = "\n".join(canonical).sha256_text()
			result[family+"_outside_triangles"] = protected.size()/36
			result[family+"_outside_sha256"] = protected.to_byte_array().hex_encode().sha256_text()
			continue
		var hashes: Array = []
		for node: MeshInstance3D in world.meshes[family]:
			var bytes := PackedByteArray()
			for si in node.mesh.get_surface_count():
				bytes.append_array(var_to_bytes(node.mesh.surface_get_arrays(si)))
			hashes.append([str(node.position),bytes.hex_encode().sha256_text()])
		if family == "tenjin":
			result.tenjin_meshes = hashes
		else:
			result.protected_meshes[family] = hashes
	var road_hits: Array = []
	for id: String in world.data.streets:
		var st: Dictionary = world.data.streets[id]
		for i in st.pts.size()-1:
			var a := Vector2(st.pts[i][0],st.pts[i][1])
			var b := Vector2(st.pts[i+1][0],st.pts[i+1][1])
			var mid := (a+b)*0.5
			if mid.x<300 or mid.x>1400 or mid.y<320 or mid.y>1290:
				continue
			var dir := (b-a).normalized()
			for off: float in [-2.2,0.0,2.2]:
				var offset := Vector2(-dir.y,dir.x)*off
				var q := PhysicsRayQueryParameters3D.create(CityData.v3(a.x+offset.x,a.y+offset.y,1.2),CityData.v3(b.x+offset.x,b.y+offset.y,1.2))
				var hit := world.get_world_3d().direct_space_state.intersect_ray(q)
				if not hit.is_empty():
					road_hits.append([id,i,off,str(hit.position)])
	result.road_hits = road_hits
	var args := OS.get_cmdline_user_args()
	FileAccess.open(args[0],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TD210_SNAPSHOT ",args[0]," outside triangles=",retained.size()/3)
	world.free()
	quit()
