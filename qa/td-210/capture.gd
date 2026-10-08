extends Node
## Loads the actual game scene. Survey cameras are diagnostic; route frames use the unchanged ChaseCam.
## Native: Godot --path godot res://qa/td-210/capture.tscn -- --out=... --phase=before --kind=all
## Browser: exported QA entry copies this file verbatim, with a JS acknowledgement for every PNG.
var city
var viewport: Window
var camera: Camera3D
var survey: Camera3D
var phase := "before"
var kind := "all"
var out := "/tmp/td210-capture"
var sequence := 0
var records: Array = []
var hud_visibility: Dictionary = {}
var footprint_marker: MeshInstance3D
var footprint_label: Label
const SEED := 185

func _ready() -> void:
	run.call_deferred()

func option(key: String, fallback: String) -> String:
	if OS.has_feature("web"):
		var value = JavaScriptBridge.eval("new URLSearchParams(location.search).get(%s)" % JSON.stringify(key), true)
		return str(value) if value != null else fallback
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--" + key + "="):
			return arg.substr(key.length() + 3)
	return fallback

func frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame

func command(action: String, payload: Dictionary) -> void:
	sequence += 1
	payload.merge({"id": sequence, "action": action})
	JavaScriptBridge.eval("window.__td210Command=%s;" % JSON.stringify(payload), true)
	while int(JavaScriptBridge.eval("window.__td210Ack||0", true)) != sequence:
		await frames(1)

func run() -> void:
	viewport = get_tree().root
	phase = option("phase", "before")
	kind = option("kind", "all")
	out = option("out", out)
	if not OS.has_feature("web"):
		DirAccess.make_dir_recursive_absolute(out)
	seed(SEED)
	GameConfig.traffic_rng_seed = SEED
	CityTouchControls.force = true
	city = load("res://scenes/lower_city/lower_city.tscn").instantiate()
	add_child(city)
	if city.car == null:
		await city.race_prepared
	await frames(20)
	city.car.sphere.freeze = true
	city.car.set_physics_process(false)
	camera = city.car.get_node("ModelHolder/ChaseCam").get("_camera")
	survey = Camera3D.new()
	survey.name = "Td210SurveyCamera"
	survey.far = camera.far
	city.add_child(survey)
	for layer in city.find_children("*", "CanvasLayer", true, false):
		hud_visibility[layer] = layer.visible
	if kind in ["all", "lots", "overhead"]:
		await lot_survey()
	if kind in ["all", "routes"]:
		await routes()
	var result := {"phase": phase, "source": option("source", "unrecorded"), "seed": SEED,
		"engine": Engine.get_version_info(), "web": OS.has_feature("web"), "frames": records,
		"world_stats": city.world.stats, "physical_phone": false,
		"scope": "Actual Lower City with production traffic/peds; fixed parked diagnostic cameras, not a driven performance claim."}
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.__td210Result=%s;" % JSON.stringify(result), true)
	else:
		FileAccess.open(out.path_join("result.json"), FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
	print("TD210_CAPTURE_DONE ", records.size())
	city.queue_free()
	await frames(3)
	if not OS.has_feature("web"):
		get_tree().quit()

func size_to(size: Vector2i) -> void:
	if OS.has_feature("web"):
		await command("viewport", {"size": [size.x, size.y]})
	else:
		viewport.size = size
	viewport.content_scale_size = Vector2i(1280, 720)
	viewport.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	viewport.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_EXPAND
	await frames(4)

func hud(show_hud: bool) -> void:
	for layer in hud_visibility:
		if is_instance_valid(layer):
			layer.visible = hud_visibility[layer] if show_hud else false
	if show_hud:
		city.touch.visible = viewport.size.x < 1000

func park(p: Vector2, heading: Vector2, settle := 45) -> void:
	var h: float = city.world.surface_h(p.x, p.y, 30.0)
	var road := CityData.v3(p.x, p.y, h)
	city.place_car(road, CityData.yaw_of(heading.x, heading.y))
	city.car.sphere.freeze = true
	city.car.sphere.global_position = road + Vector3.UP * 0.5
	city.car.model_holder.global_position = road - Vector3.UP * 0.15
	city.car.reset_physics_interpolation()
	for i in settle:
		await get_tree().physics_frame

func v3(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func snap(path: String, metadata: Dictionary) -> void:
	await frames(3)
	await RenderingServer.frame_post_draw
	var active := viewport.get_camera_3d()
	var record := {"file": path, "viewport": [viewport.size.x, viewport.size.y],
		"camera": {"position": v3(active.global_position), "basis": [v3(active.global_basis.x), v3(active.global_basis.y), v3(active.global_basis.z)], "fov": active.fov, "near": active.near},
		"car": v3(city.car.model_holder.global_position),
		"draw_calls": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
		"triangles": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),
		"objects": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME),
		"host_frame_ms": Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0}
	record.merge(metadata)
	records.append(record)
	var img := viewport.get_texture().get_image()
	if OS.has_feature("web"):
		await command("shot", {"file": path, "png": Marshalls.raw_to_base64(img.save_png_to_buffer())})
	else:
		DirAccess.make_dir_recursive_absolute(out.path_join(path.get_base_dir()))
		img.save_png(out.path_join(path))
	print("TD210_SHOT ", JSON.stringify(record))

func lot_survey() -> void:
	await size_to(Vector2i(960, 960))
	hud(false)
	survey.projection = Camera3D.PROJECTION_ORTHOGONAL
	var dressing := CityDressing.new(city.world)
	var first := int(option("first", "0"))
	var limit := int(option("limit", "1000"))
	var captured := 0
	for li in city.world.data.lots.size():
		var lot: Dictionary = city.world.data.lots[li]
		if lot.d != "kamome" or li < first:
			continue
		var fr := dressing.frontage(lot)
		if fr.is_empty():
			# A real street still supplies the survey orientation; record fallback explicitly.
			var longest := 0.0
			var center := Vector2.ZERO
			for q in lot.p:
				center += Vector2(q[0], q[1]) / float(lot.p.size())
			for k in lot.p.size():
				var a := Vector2(lot.p[k][0], lot.p[k][1])
				var b := Vector2(lot.p[(k + 1) % lot.p.size()][0], lot.p[(k + 1) % lot.p.size()][1])
				if a.distance_to(b) <= longest:
					continue
				longest = a.distance_to(b)
				var n := Vector2(-(b-a).y, (b-a).x).normalized()
				if n.dot((a+b)*0.5-center) < 0.0:
					n = -n
				fr = [a, b, n, 12.0, 12.0]
		var mid: Vector2 = (fr[0] + fr[1]) * 0.5
		var n: Vector2 = fr[2]
		var dist: float = minf(float(fr[3]) * 1.55, 24.0)
		var p := mid + n * dist
		await park(p, -n, 12)
		survey.current = true
		var target := CityData.v3(mid.x, mid.y, float(lot.h) * 0.5 + float(lot.b))
		survey.size = maxf(float(lot.h) + 7.0, (fr[0] as Vector2).distance_to(fr[1]) + 7.0)
		survey.look_at_from_position(CityData.v3(p.x, p.y, target.y), target)
		var folder := "lots"
		var view := "fixed front orthographic lot survey"
		if kind == "overhead":
			var box := Rect2(Vector2(lot.p[0][0],lot.p[0][1]),Vector2.ZERO)
			for q in lot.p: box = box.expand(Vector2(q[0],q[1]))
			var c := box.get_center()
			survey.size = maxf(box.size.x,box.size.y)+8.0
			var ground := CityData.v3(c.x,c.y,lot.b)
			survey.look_at_from_position(ground+Vector3.UP*80.0,ground,Vector3.FORWARD)
			mark_footprint(lot,li)
			folder = "lots-overhead"
			view = "diagnostic overhead with cyan target-footprint outline; adjoining buildings obscure some front surveys"
		await snap("%s/%04d/td-210-criterion-1-%s.png" % [folder,li,phase], {"lot": li, "street": lot.f, "view": view, "ortho_size": survey.size, "hud": false, "height_m": lot.h})
		captured += 1
		if captured >= limit:
			break

func routes() -> void:
	# Actual authored Kamome main/side streets, sampled on their road geometry.
	var stations := [["kamome", 840.0, 745.0, 0.0, 1.0], ["seri1", 820.0, 470.0, -1.0, 0.0], ["seri3", 880.0, 930.0, -1.0, 0.0], ["seri5", 730.0, 1240.0, -1.0, 0.0], ["uogashi1", 640.0, 525.0, 0.0, 1.0], ["uogashi2b", 760.0, 755.0, 0.0, -1.0], ["uogashi3", 940.0, 645.0, 0.0, 1.0], ["uogashi4", 1020.0, 885.0, 0.0, -1.0], ["reizo", 680.0, 1040.0, 1.0, 0.0], ["uroko", 590.0, 582.5, 0.8, 0.6], ["ichiba", 755.0, 620.0, 1.0, 0.0], ["kori", 880.0, 990.0, 1.0, 0.0]]
	for size in [Vector2i(1280, 720), Vector2i(844, 390)]:
		await size_to(size)
		for s in stations:
			if size.x < 1000 and s[0] not in ["kamome", "seri3"]:
				continue
			var road_width := 0.0
			var nearest := INF
			for road in city.world.data.roads:
				if road.street != s[0]: continue
				for j in range(road.pts.size()-1):
					var a := Vector2(road.pts[j][0],road.pts[j][1])
					var b := Vector2(road.pts[j+1][0],road.pts[j+1][1])
					var at := Geometry2D.get_closest_point_to_segment(Vector2(s[1],s[2]),a,b)
					var distance := at.distance_squared_to(Vector2(s[1],s[2]))
					if distance < nearest:
						nearest=distance;road_width=float(road.w)
			assert(nearest < 0.01 and road_width>0,"Route station must lie on authored road")
			for sign_direction in [1.0, -1.0]:
				var heading: Vector2 = Vector2(s[3], s[4]) * float(sign_direction)
				var p := Vector2(s[1], s[2]) + Vector2(-heading.y, heading.x) * minf(2.2,road_width*0.20)
				for lot in city.world.data.lots:
					var poly := PackedVector2Array()
					for q in lot.p: poly.append(Vector2(q[0],q[1]))
					assert(not Geometry2D.is_point_in_polygon(p,poly),"Route sample inside lot")
				camera.current = true
				await park(p, heading)
				var fixed_camera := camera.global_transform
				for show_hud in [true, false]:
					hud(show_hud)
					camera.global_transform = fixed_camera
					var suffix := "%s-%s-%s-%s" % [s[0], "forward" if sign_direction > 0 else "reverse", "hud" if show_hud else "world", str(size.x)]
					await snap("routes/%s/td-210-criterion-2-%s.png" % [suffix, phase], {"street": s[0], "view": "actual ChaseCam, parked on authored road", "road_width_m": road_width, "lane_offset_m": minf(2.2,road_width*0.20), "hud": show_hud})

func mark_footprint(lot: Dictionary, li: int) -> void:
	if footprint_marker == null:
		footprint_marker=MeshInstance3D.new()
		city.add_child(footprint_marker)
		var mat:=ShaderMaterial.new()
		mat.shader=Shader.new()
		mat.shader.code="shader_type spatial; render_mode unshaded, fog_disabled, depth_test_disabled, cull_disabled; void fragment(){ALBEDO=vec3(0.1,0.8,1.0);}"
		footprint_marker.material_override=mat
		footprint_marker.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var layer:=CanvasLayer.new()
		layer.layer=100
		add_child(layer)
		footprint_label=Label.new()
		footprint_label.position=Vector2(16,16)
		footprint_label.add_theme_font_size_override("font_size",24)
		footprint_label.add_theme_constant_override("outline_size",8)
		footprint_label.add_theme_color_override("font_outline_color",Color.BLACK)
		layer.add_child(footprint_label)
	footprint_label.text="DIAGNOSTIC LOT %d | %s | seed185\nCyan: authored footprint; original scene and roof geometry"%[li,phase]
	var mesh:=ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for k in lot.p.size():
		var a:=CityData.v3(lot.p[k][0],lot.p[k][1],float(lot.b)+float(lot.h)+0.05)
		var b:=CityData.v3(lot.p[(k+1)%lot.p.size()][0],lot.p[(k+1)%lot.p.size()][1],a.y)
		var side:=(b-a).normalized().cross(Vector3.UP)*0.06
		for point in [a-side,b-side,b+side,a-side,b+side,a+side]:mesh.surface_add_vertex(point)
	mesh.surface_end()
	footprint_marker.mesh=mesh
