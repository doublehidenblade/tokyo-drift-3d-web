extends SceneTree
## Run from an empty directory with --main-pack <pack> -s <absolute script>; no source overlay.
const KITS := {
	"buildings":["kamome_hall"],
	"storefronts":["sengyo_stall"],
	"props":["fish_crates","hand_trucks"]}

func files(path: String) -> Dictionary:
	var result := {}
	for file: String in DirAccess.get_files_at(path):
		var p := path.path_join(file)
		var f := FileAccess.open(p,FileAccess.READ)
		if f != null:
			result[p] = {"bytes":f.get_length(),"sha256":FileAccess.get_sha256(p)}
	for folder: String in DirAccess.get_directories_at(path):
		result.merge(files(path.path_join(folder)))
	return result

func semantic(node: Node) -> PackedByteArray:
	var bytes := var_to_bytes([node.name,node.get_class(),node.transform if node is Node3D else null])
	if node is MeshInstance3D and node.mesh != null:
		for si in node.mesh.get_surface_count():
			# The exported surface dictionary includes generated LOD index buffers.
			var surface := RenderingServer.mesh_get_surface(node.mesh.get_rid(), si)
			bytes.append_array(var_to_bytes([node.mesh.surface_get_arrays(si),surface.get("lods", [])]))
			var m: Material = node.get_active_material(si)
			if m is StandardMaterial3D:
				var values := {}
				for key: String in ["albedo_color","roughness","metallic","transparency","cull_mode","shading_mode","emission_enabled","emission","emission_energy_multiplier","uv1_scale","uv1_offset","normal_enabled"]:
					values[key] = m.get(key)
				for key: String in ["albedo_texture","emission_texture","normal_texture","roughness_texture","metallic_texture","ao_texture"]:
					var texture: Texture2D = m.get(key)
					values[key] = texture.resource_path if texture != null else ""
				bytes.append_array(var_to_bytes(values))
	for child in node.get_children():
		bytes.append_array(semantic(child))
	return bytes

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var expected := args[0] == "after"
	var found := {}
	var loaded := {}
	for family: String in KITS:
		for id: String in KITS[family]:
			var path := "res://assets/td-186/%s/%s/%s.glb" % [family,id,id]
			found[path] = ResourceLoader.exists(path)
			loaded[path] = load(path) is PackedScene if found[path] else false
	var fuel = JSON.parse_string(FileAccess.get_file_as_string("res://data/fuel/stations.json"))
	var banned := ["res://assets/td-186/buildings/chidori_terrace/chidori_terrace.glb",
		"res://assets/td-186/storefronts/pachinko_front/pachinko_front.glb",
		"res://assets/td-186/props/sol88_tower/sol88_tower.glb","res://scenes/shuto_c1/shuto_c1.tscn",
		"res://data/shuto_c1/scene.json"]
	var excluded := {}
	for path: String in banned:
		excluded[path] = not ResourceLoader.exists(path) and not FileAccess.file_exists(path)
	var passes: bool = fuel is Array and fuel.size()==2
	for path: String in found:
		passes = passes and found[path] == expected and loaded[path] == expected
	for path: String in excluded:
		passes = passes and excluded[path]
	var result := {"phase":args[0],"passes":passes,"selected_kits_present":found,"selected_kits_load":loaded,
		"fuel_stations":fuel,"excluded":excluded,"entry":ProjectSettings.get_setting("application/run/main_scene")}
	result.files = files("res://")
	result.semantic_assets = {}
	for path: String in result.files:
		if not path.ends_with(".glb.import"):
			continue
		var asset_path := path.trim_suffix(".import")
		var packed := load(asset_path) as PackedScene
		if packed == null:
			result.semantic_assets[asset_path] = "FAILED_TO_LOAD"
			passes = false
			continue
		var node := packed.instantiate()
		result.semantic_assets[asset_path] = semantic(node).hex_encode().sha256_text()
		node.free()
	result.passes = passes
	FileAccess.open(args[1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TD210_PACK phase=",args[0]," passes=",passes," files=",result.files.size())
	quit(0 if passes else 1)
