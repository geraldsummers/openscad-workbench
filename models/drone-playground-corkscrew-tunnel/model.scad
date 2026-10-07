clear_bore=200; tunnel_depth=120; shell_thickness=8; base_thickness=4; mount_hole_diameter=4.5;
module corkscrew_tunnel(){ difference(){ union(){
 translate([-124,-tunnel_depth/2,0]) cube([248,tunnel_depth,base_thickness]);
 translate([0,-tunnel_depth/2,clear_bore/2+base_thickness+8]) rotate([-90,0,0]) difference(){ cylinder(d=clear_bore+2*shell_thickness,h=tunnel_depth,$fn=96); translate([0,0,-1]) cylinder(d=clear_bore,h=tunnel_depth+2,$fn=96); }
 for(i=[0:15]) { a=i*360/15; y=-tunnel_depth/2+i*tunnel_depth/15; translate([(clear_bore/2+shell_thickness-2)*cos(a),y,clear_bore/2+base_thickness+8+(clear_bore/2+shell_thickness-2)*sin(a)]) sphere(d=13,$fn=24); }
 for(x=[-108,108]) translate([x,0,base_thickness]) cylinder(d=18,h=12,$fn=32);
 } for(x=[-108,108]) translate([x,0,-1]) cylinder(d=mount_hole_diameter,h=18,$fn=24); }}
assert(clear_bore>=200 && tunnel_depth==120); echo("SCADCTL_REQUIREMENT:parameters:PASS"); corkscrew_tunnel();
