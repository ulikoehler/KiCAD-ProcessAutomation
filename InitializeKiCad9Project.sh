#!/bin/bash
# TechOverflow KiCAD project initializer (with project FP & SYM libraries)
# Usage: $0 <filename prefix>
if [ $# -ne 1 ]
then
    echo "Usage: $0 <filename prefix>"
    exit 1
fi

# Compute project name and path
proj=$(basename "$1")
dir=$(dirname "$1")

# Generate UUIDs
SCHEMATIC_UUID=$(uuidgen)

# Create project file
cat <<EOT > ${1}.kicad_pro
{
  "board": {
    "3dviewports": [],
    "design_settings": {
      "defaults": {
        "apply_defaults_to_fp_fields": false,
        "apply_defaults_to_fp_shapes": false,
        "apply_defaults_to_fp_text": false,
        "board_outline_line_width": 0.1,
        "copper_line_width": 0.2,
        "copper_text_italic": false,
        "copper_text_size_h": 1.5,
        "copper_text_size_v": 1.5,
        "copper_text_thickness": 0.3,
        "copper_text_upright": false,
        "courtyard_line_width": 0.05,
        "dimension_precision": 4,
        "dimension_units": 3,
        "dimensions": {
          "arrow_length": 1270000,
          "extension_offset": 500000,
          "keep_text_aligned": true,
          "suppress_zeroes": true,
          "text_position": 0,
          "units_format": 0
        },
        "fab_line_width": 0.1,
        "fab_text_italic": false,
        "fab_text_size_h": 1.0,
        "fab_text_size_v": 1.0,
        "fab_text_thickness": 0.15,
        "fab_text_upright": false,
        "other_line_width": 0.15,
        "other_text_italic": false,
        "other_text_size_h": 1.0,
        "other_text_size_v": 1.0,
        "other_text_thickness": 0.15,
        "other_text_upright": false,
        "pads": {
          "drill": 0.8,
          "height": 1.27,
          "width": 2.54
        },
        "silk_line_width": 0.15,
        "silk_text_italic": false,
        "silk_text_size_h": 1.0,
        "silk_text_size_v": 1.0,
        "silk_text_thickness": 0.15,
        "silk_text_upright": false,
        "zones": {
          "min_clearance": 0.5
        }
      },
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "meta": {
        "version": 2
      },
      "rule_severities": {
        "annular_width": "error",
        "clearance": "error",
        "connection_width": "warning",
        "copper_edge_clearance": "error",
        "copper_sliver": "warning",
        "courtyards_overlap": "error",
        "creepage": "error",
        "diff_pair_gap_out_of_range": "error",
        "diff_pair_uncoupled_length_too_long": "error",
        "drill_out_of_range": "error",
        "duplicate_footprints": "warning",
        "extra_footprint": "warning",
        "footprint": "error",
        "footprint_filters_mismatch": "ignore",
        "footprint_symbol_mismatch": "warning",
        "footprint_type_mismatch": "ignore",
        "hole_clearance": "error",
        "hole_to_hole": "warning",
        "holes_co_located": "warning",
        "invalid_outline": "error",
        "isolated_copper": "warning",
        "item_on_disabled_layer": "error",
        "items_not_allowed": "error",
        "length_out_of_range": "error",
        "lib_footprint_issues": "warning",
        "lib_footprint_mismatch": "warning",
        "malformed_courtyard": "error",
        "microvia_drill_out_of_range": "error",
        "mirrored_text_on_front_layer": "warning",
        "missing_courtyard": "ignore",
        "missing_footprint": "warning",
        "net_conflict": "warning",
        "nonmirrored_text_on_back_layer": "warning",
        "npth_inside_courtyard": "ignore",
        "padstack": "warning",
        "pth_inside_courtyard": "ignore",
        "shorting_items": "error",
        "silk_edge_clearance": "warning",
        "silk_over_copper": "warning",
        "silk_overlap": "warning",
        "skew_out_of_range": "error",
        "solder_mask_bridge": "error",
        "starved_thermal": "error",
        "text_height": "warning",
        "text_on_edge_cuts": "error",
        "text_thickness": "warning",
        "through_hole_pad_without_hole": "error",
        "too_many_vias": "error",
        "track_angle": "error",
        "track_dangling": "warning",
        "track_segment_length": "error",
        "track_width": "error",
        "tracks_crossing": "error",
        "unconnected_items": "error",
        "unresolved_variable": "error",
        "via_dangling": "warning",
        "zones_intersect": "error"
      },
      "rules": {
        "max_error": 0.005,
        "min_clearance": 0.0,
        "min_connection": 0.0,
        "min_copper_edge_clearance": 0.5,
        "min_groove_width": 0.0,
        "min_hole_clearance": 0.25,
        "min_hole_to_hole": 0.25,
        "min_microvia_diameter": 0.2,
        "min_microvia_drill": 0.1,
        "min_resolved_spokes": 2,
        "min_silk_clearance": 0.0,
        "min_text_height": 0.8,
        "min_text_thickness": 0.08,
        "min_through_hole_diameter": 0.3,
        "min_track_width": 0.0,
        "min_via_annular_width": 0.1,
        "min_via_diameter": 0.5,
        "solder_mask_clearance": 0.0,
        "solder_mask_min_width": 0.0,
        "solder_mask_to_copper_clearance": 0.0,
        "use_height_for_length_calcs": true
      },
      "teardrop_options": [
        {
          "td_onpthpad": true,
          "td_onroundshapesonly": false,
          "td_onsmdpad": true,
          "td_ontrackend": false,
          "td_onvia": true
        }
      ],
      "teardrop_parameters": [
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_round_shape",
          "td_width_to_size_filter_ratio": 0.9
        },
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_rect_shape",
          "td_width_to_size_filter_ratio": 0.9
        },
        {
          "td_allow_use_two_tracks": true,
          "td_curve_segcount": 0,
          "td_height_ratio": 1.0,
          "td_length_ratio": 0.5,
          "td_maxheight": 2.0,
          "td_maxlen": 1.0,
          "td_on_pad_in_zone": false,
          "td_target_name": "td_track_end",
          "td_width_to_size_filter_ratio": 0.9
        }
      ],
      "track_widths": [],
      "tuning_pattern_settings": {
        "diff_pair_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 1.0
        },
        "diff_pair_skew_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 0.6
        },
        "single_track_defaults": {
          "corner_radius_percentage": 80,
          "corner_style": 1,
          "max_amplitude": 1.0,
          "min_amplitude": 0.2,
          "single_sided": false,
          "spacing": 0.6
        }
      },
      "via_dimensions": [],
      "zones_allow_external_fillets": false
    },
    "ipc2581": {
      "dist": "",
      "distpn": "",
      "internal_id": "",
      "mfg": "",
      "mpn": ""
    },
    "layer_pairs": [],
    "layer_presets": [],
    "viewports": []
  },
  "boards": [],
  "cvpcb": {
    "equivalence_files": []
  },
  "erc": {
    "erc_exclusions": [],
    "meta": {
      "version": 0
    },
    "pin_map": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        2,
        0,
        1,
        0,
        0,
        1,
        0,
        2,
        2,
        2,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        1,
        2
      ],
      [
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        2,
        1,
        1,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        2
      ],
      [
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        2
      ],
      [
        0,
        0,
        0,
        1,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        2
      ],
      [
        0,
        2,
        1,
        2,
        0,
        0,
        1,
        0,
        2,
        2,
        2,
        2
      ],
      [
        0,
        2,
        0,
        1,
        0,
        0,
        1,
        0,
        2,
        0,
        0,
        2
      ],
      [
        0,
        2,
        1,
        1,
        0,
        0,
        1,
        0,
        2,
        0,
        0,
        2
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ]
    ],
    "rule_severities": {
      "bus_definition_conflict": "error",
      "bus_entry_needed": "error",
      "bus_to_bus_conflict": "error",
      "bus_to_net_conflict": "error",
      "conflicting_netclasses": "error",
      "different_unit_footprint": "error",
      "different_unit_net": "error",
      "duplicate_reference": "error",
      "duplicate_sheet_names": "error",
      "endpoint_off_grid": "warning",
      "extra_units": "error",
      "footprint_filter": "ignore",
      "footprint_link_issues": "warning",
      "four_way_junction": "ignore",
      "global_label_dangling": "warning",
      "hier_label_mismatch": "error",
      "label_dangling": "error",
      "label_multiple_wires": "warning",
      "lib_symbol_issues": "warning",
      "lib_symbol_mismatch": "warning",
      "missing_bidi_pin": "warning",
      "missing_input_pin": "warning",
      "missing_power_pin": "error",
      "missing_unit": "warning",
      "multiple_net_names": "warning",
      "net_not_bus_member": "warning",
      "no_connect_connected": "warning",
      "no_connect_dangling": "warning",
      "pin_not_connected": "error",
      "pin_not_driven": "error",
      "pin_to_pin": "warning",
      "power_pin_not_driven": "error",
      "same_local_global_label": "warning",
      "similar_label_and_power": "warning",
      "similar_labels": "warning",
      "similar_power": "warning",
      "simulation_model_issue": "ignore",
      "single_global_label": "ignore",
      "unannotated": "error",
      "unconnected_wire_endpoint": "warning",
      "unit_value_mismatch": "error",
      "unresolved_variable": "error",
      "wire_dangling": "error"
    }
  },
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "test.kicad_pro",
    "version": 3
  },
  "net_settings": {
    "classes": [
      {
        "bus_width": 12,
        "clearance": 0.2,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.2,
        "line_style": 0,
        "microvia_diameter": 0.3,
        "microvia_drill": 0.1,
        "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "priority": 2147483647,
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3,
        "wire_width": 6
      }
    ],
    "meta": {
      "version": 4
    },
    "net_colors": null,
    "netclass_assignments": null,
    "netclass_patterns": []
  },
  "pcbnew": {
    "last_paths": {
      "gencad": "",
      "idf": "",
      "netlist": "",
      "plot": "",
      "pos_files": "",
      "specctra_dsn": "",
      "step": "",
      "svg": "",
      "vrml": ""
    },
    "page_layout_descr_file": ""
  },
  "schematic": {
    "annotate_start_num": 0,
    "bom_export_filename": "${PROJECTNAME}.csv",
    "bom_fmt_presets": [],
    "bom_fmt_settings": {
      "field_delimiter": ",",
      "keep_line_breaks": false,
      "keep_tabs": false,
      "name": "CSV",
      "ref_delimiter": ",",
      "ref_range_delimiter": "",
      "string_delimiter": "\""
    },
    "bom_presets": [],
    "bom_settings": {
      "exclude_dnp": false,
      "fields_ordered": [
        {
          "group_by": false,
          "label": "Reference",
          "name": "Reference",
          "show": true
        },
        {
          "group_by": true,
          "label": "Value",
          "name": "Value",
          "show": true
        },
        {
          "group_by": false,
          "label": "Datasheet",
          "name": "Datasheet",
          "show": true
        },
        {
          "group_by": false,
          "label": "Footprint",
          "name": "Footprint",
          "show": true
        },
        {
          "group_by": false,
          "label": "Qty",
          "name": "",
          "show": true
        },
        {
          "group_by": true,
          "label": "DNP",
          "name": "",
          "show": true
        }
      ],
      "filter_string": "",
      "group_symbols": true,
      "include_excluded_from_bom": false,
      "name": "Grouped By Value",
      "sort_asc": true,
      "sort_field": "Referenz"
    },
    "connection_grid_size": 50.0,
    "drawing": {
      "dashed_lines_dash_length_ratio": 12.0,
      "dashed_lines_gap_length_ratio": 3.0,
      "default_line_thickness": 6.0,
      "default_text_size": 50.0,
      "field_names": [],
      "intersheets_ref_own_page": false,
      "intersheets_ref_prefix": "",
      "intersheets_ref_short": false,
      "intersheets_ref_show": false,
      "intersheets_ref_suffix": "",
      "junction_size_choice": 3,
      "label_size_ratio": 0.25,
      "operating_point_overlay_i_precision": 3,
      "operating_point_overlay_i_range": "~A",
      "operating_point_overlay_v_precision": 3,
      "operating_point_overlay_v_range": "~V",
      "overbar_offset_ratio": 1.23,
      "pin_symbol_size": 0.0,
      "text_offset_ratio": 0.08
    },
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": {
      "version": 1
    },
    "net_format_name": "",
    "page_layout_descr_file": "",
    "plot_directory": "",
    "space_save_all_events": true,
    "spice_current_sheet_as_root": false,
    "spice_external_command": "spice \"%I\"",
    "spice_model_current_sheet_as_root": true,
    "spice_save_all_currents": false,
    "spice_save_all_dissipations": false,
    "spice_save_all_voltages": false,
    "subpart_first_id": 65,
    "subpart_id_separator": 0
  },
  "sheets": [
    [
      "b0c1ac84-aac8-4841-ad64-f219e59ce713",
      "Root"
    ]
  ],
  "text_variables": {}
}
EOT

# Create schematic file
cat <<EOT > ${1}.kicad_sch
(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "${SCHEMATIC_UUID}")
	(paper "A4")
	(lib_symbols)
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
EOT

cat <<EOT > ${1}.kicad_pcb
(kicad_pcb
	(version 20241229)
	(generator "pcbnew")
	(generator_version "9.0")
	(general
		(thickness 1.6)
		(legacy_teardrops no)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
		(39 "User.1" user)
		(41 "User.2" user)
		(43 "User.3" user)
		(45 "User.4" user)
		(47 "User.5" user)
		(49 "User.6" user)
		(51 "User.7" user)
		(53 "User.8" user)
		(55 "User.9" user)
	)
	(setup
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting front back)
		(pcbplotparams
			(layerselection 0x00000000_00000000_55555555_5755f5ff)
			(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)
			(disableapertmacros no)
			(usegerberextensions no)
			(usegerberattributes yes)
			(usegerberadvancedattributes yes)
			(creategerberjobfile yes)
			(dashed_line_dash_ratio 12.000000)
			(dashed_line_gap_ratio 3.000000)
			(svgprecision 4)
			(plotframeref no)
			(mode 1)
			(useauxorigin no)
			(hpglpennumber 1)
			(hpglpenspeed 20)
			(hpglpendiameter 15.000000)
			(pdf_front_fp_property_popups yes)
			(pdf_back_fp_property_popups yes)
			(pdf_metadata yes)
			(pdf_single_document no)
			(dxfpolygonmode yes)
			(dxfimperialunits yes)
			(dxfusepcbnewfont yes)
			(psnegative no)
			(psa4output no)
			(plot_black_and_white yes)
			(sketchpadsonfab no)
			(plotpadnumbers no)
			(hidednponfab no)
			(sketchdnponfab yes)
			(crossoutdnponfab yes)
			(subtractmaskfromsilk no)
			(outputformat 1)
			(mirror no)
			(drillshape 1)
			(scaleselection 1)
			(outputdirectory "")
		)
	)
	(net 0 "")
	(embedded_fonts no)
)
EOT

#
# Create schematic symbol library mapping
#
mkdir -p ${dir}/libraries
cat <<EOT > ${dir}/sym-lib-table
(sym_lib_table
  (lib (name "${proj}")(type "KiCad")(uri "\${KIPRJMOD}/libraries/${proj}.kicad_sym")(options "")(descr ""))
)
EOT

cat <<EOT > ${dir}/libraries/${proj}.kicad_sym
(kicad_symbol_lib (version 20211014) (generator kicad_converter))
EOT

#
# Create footprint library mapping (just an empty directory)
#
mkdir -p ${dir}/libraries/footprints
# Avoid empty directory (so it's not ignored by git)
touch ${dir}/libraries/footprints/.gitignore

cat <<EOT > ${dir}/fp-lib-table
(fp_lib_table
  (lib (name ${proj})(type KiCad)(uri \${KIPRJMOD}/libraries/footprints)(options "")(descr ""))
)
EOT

#
# Create directory for 3D models.
# The search path might need to be configured manually
# since it's not stored in a project
#
mkdir -p ${dir}/libraries/3D
# Avoid empty directory (so it's not ignored by git)
touch ${dir}/libraries/3D/.gitignore

#
# Create .gitignore
#
cat <<EOT > .gitignore
*-bak
*-backups
*-cache*
*-bak*
_autosave*
\#auto_saved_files\#
*.lck
EOT
