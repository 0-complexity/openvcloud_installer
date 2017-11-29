@0x89a7619448a71e6b;

struct Schema {
    nodes @0 : List(Text); # kubernetes_node producer services
    master @1 : Text; # optional master service
    controller @2 : Text; # optional controller service
}