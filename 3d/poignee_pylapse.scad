/********************************************************
* pylapse - poignée
*
*   Olivier Boesch (c) 2020
*
*   v1 : version initiale
*   v2 : changement visserie M3 -> M4
********************************************************/
$fn = $preview?50:300;


type_tete = "r"; //r->rond, h->hex (d_ecrou -> Mx + tolérance)
d_ecrou = 7.8;
h_ecrou = 3;
d_tige = 4.2;

d_cyl_ext = 12;
h_cyl_ext = 5;

d_cran=4;
step_cran=45;
prof_cran = d_cran/6;

translate([0,0,h_cyl_ext/2]) difference(){
    //poignée
    cylinder(d=d_cyl_ext,h=h_cyl_ext,center=true);
    //tête
    if( type_tete == "h"){
        translate([0,0,h_cyl_ext/2-h_ecrou/2]) cylinder(d=d_ecrou*2/sqrt(3),h=h_ecrou+1,$fn=6,center=true);
    }
    else{
        translate([0,0,h_cyl_ext/2-h_ecrou/2]) cylinder(d=d_ecrou,h=h_ecrou+1,center=true);
    }
    //tige
    cylinder(d=d_tige,h=h_cyl_ext+2,center=true);
    //crans
    for(angle=[0:step_cran:360]){
        rotate([0,0,angle]) translate([d_cyl_ext/2+d_cran/2-prof_cran,0,0]) cylinder(d=d_cran,h=h_cyl_ext+2, center=true);
    }
}