/**********************

Pylapse : Mount for a raspberry pi 3b+ case
on laboratory support (diameter 10mm approx)

***********************/

use <PiHole.scad>
use <MCAD/nuts_and_bolts.scad>

$fn=150;

//board mount
module board_mount(pos=[0,0,0]){
    translate(pos){
        difference(){
            cube([95,77,40],center=true);
            //screw and nuts holes
            translate([-37.5,-75/2+5,-10.5]) cylinder(d=4.5,h=20,center=true);
            translate([-37.5,-75/2+5,-40/2+5])nutHole(4, tolerance = +0.05);
            translate([37.5,-75/2+5,-10.5]) cylinder(d=4.5,h=20,center=true);
            translate([37.5,-75/2+5,-40/2+5]) nutHole(4, tolerance = +0.05);
            //vertical bar
            translate([0,0,20]) rotate([90,45,0]) cube([42,42,80], center=true);
            translate([0,-20,13]) cube([80,16,25], center=true);
            translate([-30,-20,0]) cylinder(d=5.5,h=45,center=true);
            translate([30,-20,0]) cylinder(d=5.5,h=45,center=true);
            translate([-30,-20,-18.5]) cylinder(d=10.5,h=4,center=true);
            translate([30,-20,-18.5]) cylinder(d=10.5,h=4,center=true);
            translate([-30,-20,15.5]) cylinder(d=26,h=10,center=true);
            translate([30,-20,15.5]) cylinder(d=26,h=10,center=true);
            //horizontal bar
            translate([0,22,12]) rotate([0,90,0]) cube([10.5,10.2,100], center=true);
            translate([95/2-10,40,12]) rotate([90,0,0]) cylinder(d=4.5,h=30,center=true);
            translate([95/2-11.8,32,5]) linear_extrude(20) nutHole(4, tolerance = 0.1, proj=2);
            
        }
    }
}

module vertical_lock(){
    difference(){
        cube([78,14,10], center=true);
        translate([-30,0,0]) cylinder(d=5.5,h=45,center=true);
        translate([30,0,0]) cylinder(d=5.5,h=45,center=true);
    }
}

//cam mount
module camera_mount(pos=[0,0,0]){
    translate(pos){
        difference(){
            cube([32,32,3], center=true);
            translate([0,-5,0]) cylinder(d=5, h=6, center=true);
            translate([0,5,0]) cylinder(d=5, h=6,center=true);
            translate([0,0,2]) cube([5,5+5,4],center=true);
            translate([0,0,-6]) cube([40,10.5,10.5],center=true);
        }
    }
}



//render
board_mount();
if($preview) {
    translate([140,28,12]) rotate([-90,0,0]) camera_mount();
    translate([0,-20,10]) vertical_lock();
    color("red", 0.2){
        translate([40,22,12]) rotate([0,90,0]) cube([10,10,250], center=true);
        translate([0,0,-2.5]) rotate([90,0,0]) cylinder(d=10,h=100,center=true);
        
    }
}
else{
    translate([0,100,0]) rotate([0,180,0]) camera_mount();
    translate([0,60,0]) vertical_lock();
}