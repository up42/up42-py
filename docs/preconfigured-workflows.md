# Preconfigured workflows

Some example workflows to use with the UP42 Python SDK.

### Ship-Identification

<img align="leff" src="https://metadata.up42.com/54217695-73f4-4528-a575-a429e9af6568/Block_Thumbnail_Ship_Identification1590606665498.png" alt="" width="120"/>

blockdiag {
   fontsize=10
   
   A -> B -> C -> D;
   
   A[label="Spot", numbered = 1];
   B[label="Tiling", numbered = 2];
   C[label="Ship-Detection", numbered = 3];
   D[label="Ship-Identification", numbered = 4];
}


blockdiag {
   A [numbered = 1, label = "Input", description = "Beef, carrots, potatoes, curry powder and water"];
   B [numbered = 2, label = "Process", description = "Simmer and simmer"];
   C [numbered = 3, label = "Output", description = "yum-yum curry"];

   A -> B -> C;
   
}