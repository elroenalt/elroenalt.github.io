
import JSZip from 'https://esm.sh/jszip@3.10.1';
let definitions_json;
let default_json;
const dimension_container = document.querySelector('#hirachy')
let dimensions = {
}
let editor;
let display;
let quickCreator; 
async function loadGameData() {
    try {
        const response1 = await fetch('assets/default.json');
        const data1 = await response1.json();
        default_json = data1
        
        const response2 = await fetch('assets/def.json');
        const data2 = await response2.json();
        definitions_json = data2
        editor = new Editor()
        display = new Display()
        quickCreator = new QuickCreator()

        document.querySelector('#download').addEventListener('click', () => {
            downloadAllDimensions()
        })
        resizeCanvas()
        document.addEventListener('keydown', (event) => {
            const key = event.key?.toLowerCase();
            if (!key) return;
            switch (key) {
                case 'escape':
                    for (let dim of Object.values(dimensions)) {
                        dim.html["properties_frame"].style.display = "none"
                        editor.focus(false,false)
                    }
                    break;
            }
        });
    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}
function resizeCanvas() {
    if (!display) return;
    const canvas = document.querySelector('#canvas');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    display.draw_universe()
}
class Dimension {
    constructor(file_path,properties) {
        this.file_path = file_path
        this.properties = properties
        this.render = true
        console.log(properties)
        this.load()
    }
    centerPlanet() {
        let x = 0;
        let y = 0;
        let props = this.properties;

        const scale = ((1/6)* display.width/ (this.properties["earthRadiusMultiplier"] * display.AU_to_earthRadius ))
        display.scale = scale

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"] && parent["parentDimensionId"] != parent["dimensionId"]) {
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);
        }
        display.camera = [x,y]
        display.draw_universe()
    }
    load() {
        const container = document.createElement('div')
        container.className = "dimension_container"

        this.html = {
            "name": Object.assign(document.createElement('div'), {
                className: "dimension_name",
                textContent: this.properties["name"]
            }),
            "view": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_edit",
                textContent: "☑"
            }),
            "reload": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_reload",
                textContent: "🗘"
            }),
            "remove": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_remove",
                textContent: "🗑"
            }),
            "file_path": Object.assign(document.createElement('div'), {
                className: "dimension_file_path",
                textContent: this.file_path
            })
        }
        for (let item of Object.values(this.html)) {
            container.appendChild(item);
        }
        this.html["remove"].addEventListener('click',() => {
            this.html["container"].remove()
            this.html["properties_frame"].remove()
            delete dimensions[this.file_path]
            display.draw_universe()
            })
        this.html["reload"].addEventListener('click',() => {
            this.html["properties_frame"].remove()
            this.load_properties()
            })
        this.html["view"].addEventListener('click',() => {
            this.html["view"].textContent = this.html["view"].textContent == "☑" ? "☐" : "☑"
            this.render = !this.render
            display.draw_universe()
            })
        this.html["file_path"].addEventListener('click', () => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            this.toggle_properties()
            })
        this.html["name"].addEventListener('click', () => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            this.toggle_properties()})
        this.html["container"] = container
        dimension_container.appendChild(container)
        this.load_properties()
    }

    load_properties() {
        const properties_frame = Object.assign(document.createElement('div'), {
            className: "dimension_properties",
        })
        let properties = {}
        console.log(typeof(default_json))
        console.log(Object.keys(default_json))
        for (let item of Object.keys(default_json)) {
            console.log(item)
            if (this.properties[item]) {
                properties[item] = this.properties[item]
            }else {
                properties[item] = default_json[item]
            }
            if(item == "customSeaFluid" && !properties[item]) {
                properties[item] =  {
                    "namespace": "adv_rocketry",
                    "path": null
                }
            }
        }
        this.properties = properties
        this.html["properties"] = []
        for (let item of Object.entries(this.properties)) {
            const element = Object.assign(document.createElement('div'), {
                className: "dimension_property",
                textContent: item[0]
            })
            element.addEventListener("click", () => {
                editor.focus(this.file_path,item[0])
                const propInfo = definitions_json[item[0]];
                if (!propInfo || propInfo["extra"] !== "color") {
                    this.centerPlanet()
                }
            })
            properties_frame.appendChild(element)
            this.html["properties"].push(element)
        }
        dimension_container.appendChild(properties_frame)
        properties_frame.style.display = "none"
        this.html["properties_frame"] = properties_frame
    }
    toggle_properties() {
        const display = this.html["properties_frame"]
        if (display.style.display === 'none') {
            display.style.display = "block"
        }else {
            display.style.display = "none"
        }
    }
}
async function downloadAllDimensions() {
    const zip = new JSZip();

    for (const planet of Object.values(dimensions)) {
        const name = planet.file_path
        const fileName = `${name}.json`;
        const properties = planet.properties
        if(!properties["customSeaFluid"]["namespace"] || !properties["customSeaFluid"]["path"]) {
            properties["customSeaFluid"] = null
        }
        const fileContent = JSON.stringify(properties, null, 4);
        
        zip.file(fileName, fileContent);
    }

    const content = await zip.generateAsync({ type: "blob" });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(content);
    link.download = "dimensionProperties.zip"; 
    
    document.body.appendChild(link);
    link.click();

    setTimeout(() => {
        URL.revokeObjectURL(link.href);
        link.remove();
    }, 200);
}
class Display {
    constructor() {
        this.tooltip = document.querySelector('#tooltip');
        this.planets = []
        this.canvas = document.querySelector('#canvas')
        this.ctx = this.canvas.getContext("2d");
        this.focus = null
        this.old_width = 0
        this.speed = 3
        this.camera = [0,0]
        this.scale = 10
        this.AU_to_earthRadius = 1/2343
        this.orbit_col = ["#b6c60e","#4d2911","#5A5A5A","#b6c60e","#4d2911","#5A5A5A"]
        this.mode = "draw"
        this.focus_color = false
        this.ring_width = 0.05
        this.ring_dist = 0.1
        this.mouse_focus = null
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            let isFocus = false
            for(let planet of this.planets) {
                const dx = planet.pos[0] - x
                const dy = planet.pos[1] - y
                const d = Math.sqrt(dx**2+dy**2)
                if (d < planet.radius) {
                    isFocus = true
                    this.tooltip.style.display = "block"
                    const Tx = e.clientX + 15; 
                    const Ty = e.clientY + 15;
                    this.tooltip.style.transform = `translate(${Tx}px, ${Ty}px)`;
                    this.tooltip.textContent = planet.file_path
                    this.mouse_focus = planet
                }
            }
            if (!isFocus) {
                this.tooltip.style.display = 'none';
            }
        });
        this.canvas.addEventListener('click', () => {
            if (this.mouse_focus) {
                if (dimensions[this.mouse_focus.file_path].html["properties_frame"].style.display == "none") {
                    dimensions[this.mouse_focus.file_path].html["properties_frame"].style.display = "block"
                }
                dimensions[this.mouse_focus.file_path].centerPlanet()
                editor.focus(false,false)
            }
        });
        this.canvas.addEventListener('mouseout', () => {
            this.tooltip.style.display = 'none';
        });
        this.canvas.addEventListener('keydown', (event) => {
            const key = event.key.toLowerCase();
            const moveStep = this.speed / this.scale;
            switch (key) {
                case 'arrowup':
                    this.camera[1] -= moveStep
                    break;
                case 'arrowdown':
                    this.camera[1] += moveStep
                    break;
                case 'arrowleft':
                    this.camera[0] -= moveStep
                    break;
                case 'arrowright':
                    this.camera[0] += moveStep
                    break;
                case 'o':
                    this.scale *= 1.1
                    break;
                case 'p':
                    this.scale /= 1.1
                    break;
            }
            this.draw_universe()
        });
    }
    draw_color(color) {
        this.planets = []
        this.mouse_focus = null
        this.width = this.canvas.width
        this.height = this.canvas.height
        this.ctx.clearRect(0,0,this.width   ,this.height)
        const SDR = [color.x/(1+color.x),color.y/(1+color.y),color.z/(1+color.z)]
        const RGB = [SDR[0]*255,SDR[1]*255,SDR[2]*255]
        this.ctx.fillStyle = `rgb(${RGB[0]},${RGB[1]},${RGB[2]})`
        this.ctx.fillRect(0,0,this.width,this.height)
    }
    draw_universe() {
        this.planets = []
        this.mouse_focus = null
        this.width = this.canvas.width
        this.height = this.canvas.height
        this.cx = this.width/ 2
        this.cy = this.height / 2
        this.ctx.clearRect(0,0,this.width   ,this.height)
        for (let dimension of Object.values(dimensions)){
            if (dimension.render) {
                this.draw_body(dimension)
            }
        }
    }
    draw_body(dim) {
        let parent_count = 0;
        let x = 0;
        let y = 0;
        let props = dim.properties;

        const raw_radius = (props["earthRadiusMultiplier"] || 1) * this.scale * this.AU_to_earthRadius;
        const radius = Math.max(1, raw_radius + 1);

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"] && parent_count < 10 && parent["parentDimensionId"] != parent["dimensionId"]) {
                parent_count += 1;
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);

            const orbX = (x - this.camera[0]+props["orbitalDistanceToParent"]) * this.scale + this.cx;
            const orbY = (y - this.camera[1]) * this.scale + this.cy;
            const orbit_radius = (props["orbitalDistanceToParent"] || 0) * this.scale;
            
            
            this.ctx.beginPath();
            //this.ctx.setLineDash([5, 5]);
            this.ctx.arc(orbX || 1, orbY || 1, orbit_radius || 1, 0, 2 * Math.PI);
            this.ctx.strokeStyle = "#ffffff";
            this.ctx.stroke();
        }
        const screenX = (x - this.camera[0]) * this.scale + this.cx;
        const screenY = (y - this.camera[1]) * this.scale + this.cy;
        const color = this.orbit_col[parent_count] || "#ffffff";

        this.ctx.beginPath();
        this.ctx.setLineDash([]);
        this.ctx.arc(screenX || 1, screenY || 1 , radius || 1, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();

        this.planets.push({
            "file_path": `${props.dimensionId.namespace}_${props.dimensionId.path}`,
            "radius": radius,
            "pos": [screenX,screenY]
        })
    }
}
class Editor {
    constructor() {
        this.info_html = {
            "name": document.querySelector('#editor-name'),
            "description": document.querySelector('#editor-description'),
            "type": document.querySelector('#editor-type')
        }
        this.inputs = [
            {
                "frame": document.querySelector('#switch-row'),
                "input": document.querySelector('#switch-input')
            },
            {
                "frame": document.querySelector('#text-row'),
                "input": document.querySelector('#text-input')
            },
            {
                "frame": document.querySelector('#vec3-row'),
                "inputs": [
                    document.querySelector('#vec1-input'),
                    document.querySelector('#vec2-input'),
                    document.querySelector('#vec3-input'),
                ]
            },
            {
                "frame": document.querySelector('#selection-row'),
                "input": document.querySelector('#selection-input'),
                "datalist": document.querySelector('#datalist')
            },
            {
                "frame": document.querySelector('#path-row'),
                "inputs": [
                    document.querySelector('#namespace-input'),
                    document.querySelector('#path-input')
                ]
            }
        ]
        this.inputs.forEach((item, i) => {
            if (!item.input && !item.inputs) console.error(`Input ${i} is NULL!`);
        });
        this.activeDim = null
        this.activeProp = null
        this.color = false
        this.setupListeners()
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
    }
    setupListeners() {
        this.inputs[0]["input"].addEventListener('change', (e) => {
            if (this.activeDim && this.activeProp) {
                dimensions[this.activeDim].properties[this.activeProp] = e.target.checked;
                
            }
        });
        this.inputs[1]["input"].addEventListener('input', (e) => {
            if (this.activeDim && this.activeProp) {
                let val = e.target.value;
                const type = definitions_json[this.activeProp]["varStruc"];
                dimensions[this.activeDim].properties[this.activeProp] = type == "int" ? Number(val) || 0 : type == "float" ? parseFloat(val) || 0.0 : String(val) || "";
                if (this.activeProp == "name" ){
                    dimensions[this.activeDim].html["name"].textContent = String(val)
                }
                
            }
        });
        const axes = ["x", "y", "z"];
        this.inputs[2]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                if (this.activeDim && this.activeProp) {
                    const axis = axes[i];
                    dimensions[this.activeDim].properties[this.activeProp][axis] = parseFloat(e.target.value) || 0.0;
                    dimensions[this.activeDim].centerPlanet()
                }
            });
        });
        const paths = ["namespace","path"];
        this.inputs[4]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                let val = String(e.target.value)
                if (this.activeDim && this.activeProp) {
                    const path = paths[i];
                    dimensions[this.activeDim].properties[this.activeProp][path] = val
                    if (this.activeProp == "dimensionId" ){
                        const dimension = dimensions[this.activeDim]
                        let file_path = [dimension.properties[this.activeProp]["namespace"],dimension.properties[this.activeProp]["path"]].join("_")
                        if (Object.keys(dimensions).includes(file_path)) {
                            return
                        }
                        delete dimensions[this.activeDim];
                        dimension.file_path = file_path
                        dimension.html.file_path.textContent = file_path
                        this.activeDim  = file_path
                        dimensions[file_path] = dimension
                    }

                }
                dimensions[this.activeDim].centerPlanet()
            });
        });
        this.inputs[3]["input"].addEventListener('input', (e) => {
            if (!this.activeDim || !this.activeProp) return;
            const rawValue = e.target.value;
            let newValue = null;

            if (rawValue && rawValue.trim() !== '' && rawValue.trim().toLowerCase() !== 'null') {
                const selectedKey = rawValue.trim();
                if (dimensions[selectedKey]) {
                    newValue = dimensions[selectedKey].properties["dimensionId"] || null;
                } else {
                    newValue = null;
                }
            }

            dimensions[this.activeDim].properties[this.activeProp] = newValue;
            dimensions[this.activeDim].centerPlanet();
        });
    }
    focus(dim,prop) {
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
        const info = prop ? definitions_json[prop] : true
        if (!info) {
            display.draw_universe()
            return
        }
        if (!prop || !dim || !Object.keys(definitions_json).includes(prop)) {
            this.info_html["name"].textContent = ""
            this.info_html["description"].textContent = "This is where you will see an property description"
            this.info_html["type"].textContent = ""
            return
        }
        this.info_html["name"].textContent = prop
        this.info_html["description"].textContent = info["definition"] 
        this.info_html["type"].textContent = info["varStruc"]
        this.activeDim = dim
        this.activeProp = prop

        let val = dimensions[dim].properties[prop]
        
        if (info["extra"] == "color") {
            display.draw_color(val)
        }else {
            display.draw_universe()
        }
        
        switch(info["varStruc"]) {
            case "float":
            case "int":
            case "str": {
                this.inputs[1]["frame"].style.display = "block";
                this.inputs[1]["input"].value = (val === null) ? "" : String(val);
                break;}
            case "boolean":{
                this.inputs[0]["frame"].style.display = "block";
                this.inputs[0]["input"].checked = val;
                break;}
            case "Vec3":{
                this.inputs[2]["frame"].style.display = "block";
                for (let i = 0; i < 3; i++) {
                    let vali = val[["x","y","z"][i]]
                    this.inputs[2]["inputs"][i].value = vali
                }
                break;}
            case "path":{
                if (info["extra"] == "selection") {
                    this.inputs[3]["frame"].style.display = "block";
                    this.inputs[3]["input"].value = val ? [val["namespace"],val["path"]].join("_") : null
                    this.inputs[3]["input"].innerHTML = "";
                    const option = document.createElement('option');
                    option.value = null;
                    option.textContent = "--none--";
                    this.inputs[3]["input"].appendChild(option);
                    Object.keys(dimensions).forEach(path => {
                        if (path != dim) {
                            const option = document.createElement('option');
                            option.value = path;
                            option.textContent = path;
                            this.inputs[3]["input"].appendChild(option);
                        }
                    });
                }else {
                    this.inputs[4]["frame"].style.display = "block";
                    this.inputs[4]["inputs"][0].value = val["namespace"]
                    this.inputs[4]["inputs"][1].value = val["path"]
                }
                break;}
            default:
                console.log("not added " + info["varStruc"])
        }
    }
}
class QuickCreator {
    constructor() {
        this.html = {
            "container": document.querySelector("#quickCreator"),
            "namespace": document.querySelector('#quickCreator-namespace'),
            "path": document.querySelector('#quickCreator-path'),
            "name": document.querySelector("#quickCreator-name"),
            "vec1": document.querySelector('#quickCreator-vec1'),
            "vec2": document.querySelector("#quickCreator-vec2"),
            "vec3": document.querySelector("#quickCreator-vec3"),
            "selection": document.querySelector("#quickCreator-selection"),
            "orbitalDistance": document.querySelector("#quickCreator-orbitalDistance"),
            "earthRadiusMultiplier": document.querySelector("#quickCreator-earthRadiusMultiplier"),
            "quickCreate": document.querySelector("#quickCreate"),
            "close": document.querySelector("#close"),
            "open": document.querySelector("#create")
        }
        this.id = 0
        this.html["open"].addEventListener('click', () => this.open());
        this.html["close"].addEventListener('click', () => {
            this.html["container"].style.display = "none"
        });
        this.html["quickCreate"].addEventListener("click", () => {
            this.quickCreate()
        })
    }
    open() {
        this.html["container"].style.display = "block"
        this.html["vec1"].value = 0.0
        this.html["vec2"].value = 0.0
        this.html["vec3"].value = 0.0
        this.html["namespace"].value = "adv_rocketry"
        this.html["path"].value = ""
        this.html["name"].value = ""
        this.html["selection"].value = null
        this.html["orbitalDistance"].value = 0.0
        this.html["earthRadiusMultiplier"].value = 0.5
        this.html["selection"].innerHTML = "";
        const option = document.createElement('option');
        option.value = null;
        option.textContent = "--None--";
        this.html["selection"].appendChild(option);
        Object.keys(dimensions).forEach(path => {
            const option = document.createElement('option');
            option.value = path;
            option.textContent = path;
            this.html["selection"].appendChild(option);
        });
    }
    quickCreate() {
        const pos = {
            "x": parseFloat(this.html["vec1"].value) || 0.0,
            "y": parseFloat(this.html["vec2"].value) || 0.0,
            "z": parseFloat(this.html["vec3"].value) || 0.0
        }
        const dimensionId = {
            "namespace":String(this.html["namespace"].value) || "adv_rocketry",
            "path": String(this.html["path"].value) || `planet${this.id}` 
        }
        let name = String(this.html["name"].value) || `Planet${this.id}` 
        const parentDimensionId = String(this.html["selection"].value) || null
        const orbitalDistance = parseFloat(this.html["orbitalDistance"].value) || 0.0
        const earthRadiusMultiplier = parseFloat(this.html["earthRadiusMultiplier"].value) || 0.0
        
        let key = `${dimensionId["namespace"]}_${dimensionId["path"]}`;
        if (Object.keys(dimensions).includes(key)) {
            key += "1"
            dimensionId["path"] += "1"
        }
        const json = structuredClone(default_json); 

        json.position = pos;
        json.name = name;
        json.dimensionId = dimensionId;
        json.parentDimensionId = Object.keys(dimensions).includes(parentDimensionId)&& parentDimensionId ? dimensions[parentDimensionId].properties["dimensionId"] : null;
        json.orbitalDistance = orbitalDistance;
        json.earthRadiusMultiplier = earthRadiusMultiplier;

        dimensions[key] = new Dimension(key, json);
        dimensions[key].centerPlanet()
        this.open()
        if (display) display.draw_universe()
        this.id += 1;
    }
}
window.addEventListener('dragenter', (e) => {
    e.preventDefault();
    document.body.classList.add('dragging');
});
window.addEventListener('dragover', (e) => {
    e.preventDefault();
});
window.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
        document.body.classList.remove('dragging');
    }
});
window.addEventListener('drop', (e) => {
    e.preventDefault();
    document.body.classList.remove('dragging');

    const items = e.dataTransfer.items;
    if (items) {
        for (let i = 0; i < items.length; i++) {
            const entry = items[i].webkitGetAsEntry();
            if (entry) {
                traverseFileTree(entry);
            }
        }
    }
});
function traverseFileTree(item, path = "") {
    if (item.isFile) {
        if (item.name.endsWith('.json')) {
            item.file((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const jsonData = JSON.parse(e.target.result);
                    path = item.name.replace(".json","")
                    dimensions[path] = new Dimension(path,jsonData)
                    if (display) display.draw_universe();
                };
                reader.readAsText(file);
            });
        }
    } else if (item.isDirectory) {
        const dirReader = item.createReader();
        dirReader.readEntries((entries) => {
            for (let entry of entries) {
                traverseFileTree(entry, path + item.name + "/");
            }
        });
    }
}
window.addEventListener('resize', resizeCanvas);
loadGameData();