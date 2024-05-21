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
        "board_outline_line_width": 0.1,
        "copper_line_width": 0.2,
        "copper_text_size_h": 1.5,
        "copper_text_size_v": 1.5,
        "copper_text_thickness": 0.3,
        "other_line_width": 0.15,
        "silk_line_width": 0.15,
        "silk_text_size_h": 1.0,
        "silk_text_size_v": 1.0,
        "silk_text_thickness": 0.15
      },
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {
        "solder_mask_clearance": 0.0,
        "solder_mask_min_width": 0.0
      },
      "track_widths": [],
      "via_dimensions": []
    },
    "ipc2581": {
      "dist": "",
      "distpn": "",
      "internal_id": "",
      "mfg": "",
      "mpn": ""
    },
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
      "global_label_dangling": "warning",
      "hier_label_mismatch": "error",
      "label_dangling": "error",
      "lib_symbol_issues": "warning",
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
      "similar_labels": "warning",
      "simulation_model_issue": "ignore",
      "unannotated": "error",
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
    "version": 1
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
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3,
        "wire_width": 6
      }
    ],
    "meta": {
      "version": 3
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
          "name": "${QUANTITY}",
          "show": true
        },
        {
          "group_by": true,
          "label": "DNP",
          "name": "${DNP}",
          "show": true
        }
      ],
      "filter_string": "",
      "group_symbols": true,
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
      "$SCHEMATIC_UUID",
      "Stammblatt"
    ]
  ],
  "text_variables": {}
}
EOT

# Create schematic file
cat <<EOT > ${1}.kicad_sch
(kicad_sch
       (version 20231120)
       (generator "eeschema")
       (generator_version "8.0")
       (uuid "$SCHEMATIC_UUID")
       (paper "A4")
       (lib_symbols)
       (sheet_instances
               (path "/"
                       (page "1")
               )
       )
)
EOT

cat <<EOT > ${1}.kicad_pcb
(kicad_pcb
        (version 20240108)
        (generator "pcbnew")
        (generator_version "8.0")
        (general
                (thickness 1.6)
                (legacy_teardrops no)
        )
        (paper "A4")
        (layers
                (0 "F.Cu" signal)
                (31 "B.Cu" signal)
                (32 "B.Adhes" user "B.Adhesive")
                (33 "F.Adhes" user "F.Adhesive")
                (34 "B.Paste" user)
                (35 "F.Paste" user)
                (36 "B.SilkS" user "B.Silkscreen")
                (37 "F.SilkS" user "F.Silkscreen")
                (38 "B.Mask" user)
                (39 "F.Mask" user)
                (40 "Dwgs.User" user "User.Drawings")
                (41 "Cmts.User" user "User.Comments")
                (42 "Eco1.User" user "User.Eco1")
                (43 "Eco2.User" user "User.Eco2")
                (44 "Edge.Cuts" user)
                (45 "Margin" user)
                (46 "B.CrtYd" user "B.Courtyard")
                (47 "F.CrtYd" user "F.Courtyard")
                (48 "B.Fab" user)
                (49 "F.Fab" user)
                (50 "User.1" user)
                (51 "User.2" user)
                (52 "User.3" user)
                (53 "User.4" user)
                (54 "User.5" user)
                (55 "User.6" user)
                (56 "User.7" user)
                (57 "User.8" user)
                (58 "User.9" user)
        )
        (setup
                (pad_to_mask_clearance 0)
                (allow_soldermask_bridges_in_footprints no)
                (pcbplotparams
                        (layerselection 0x00010fc_ffffffff)
                        (plot_on_all_layers_selection 0x0000000_00000000)
                        (disableapertmacros no)
                        (usegerberextensions no)
                        (usegerberattributes yes)
                        (usegerberadvancedattributes yes)
                        (creategerberjobfile yes)
                        (dashed_line_dash_ratio 12.000000)
                        (dashed_line_gap_ratio 3.000000)
                        (svgprecision 4)
                        (plotframeref no)
                        (viasonmask no)
                        (mode 1)
                        (useauxorigin no)
                        (hpglpennumber 1)
                        (hpglpenspeed 20)
                        (hpglpendiameter 15.000000)
                        (pdf_front_fp_property_popups yes)
                        (pdf_back_fp_property_popups yes)
                        (dxfpolygonmode yes)
                        (dxfimperialunits yes)
                        (dxfusepcbnewfont yes)
                        (psnegative no)
                        (psa4output no)
                        (plotreference yes)
                        (plotvalue yes)
                        (plotfptext yes)
                        (plotinvisibletext no)
                        (sketchpadsonfab no)
                        (subtractmaskfromsilk no)
                        (outputformat 1)
                        (mirror no)
                        (drillshape 1)
                        (scaleselection 1)
                        (outputdirectory "")
                )
        )
        (net 0 "")
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
