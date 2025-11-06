import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import DxfParser from "dxf-parser";
import { DXFEntity } from "./ObjectSelector";

interface DXFViewerProps {
  file: File | null;
  onParsed: (
    scene: THREE.Scene,
    camera: THREE.Camera,
    renderer: THREE.WebGLRenderer,
    entities: DXFEntity[]
  ) => void;
  visibleEntities?: string[];
}

export const DXFViewer = ({ file, onParsed, visibleEntities }: DXFViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const meshMapRef = useRef<Map<string, THREE.Line>>(new Map());

  useEffect(() => {
    if (!containerRef.current || !file) return;

    // Setup Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      10000
    );
    camera.position.set(0, 0, 100);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);

    // Add grid helper
    const gridHelper = new THREE.GridHelper(200, 20, 0x3b82f6, 0xe2e8f0);
    scene.add(gridHelper);

    // Parse and render DXF
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const dxfString = e.target?.result as string;
        const parser = new DxfParser();
        const dxf = parser.parseSync(dxfString);

        if (dxf && dxf.entities) {
          // Create geometry from DXF entities
          const group = new THREE.Group();
          const parsedEntities: DXFEntity[] = [];
          const meshMap = new Map<string, THREE.Line>();

          dxf.entities.forEach((entity: any, index: number) => {
            const entityId = `entity-${index}`;
            const entityData: DXFEntity = {
              id: entityId,
              type: entity.type || "UNKNOWN",
              layer: entity.layer,
              visible: true,
            };
            parsedEntities.push(entityData);
            let mesh: THREE.Line | null = null;

            if (entity.type === "LINE") {
              const material = new THREE.LineBasicMaterial({ 
                color: entity.color ? new THREE.Color(entity.color) : 0x3b82f6,
                linewidth: 2
              });
              const points = [
                new THREE.Vector3(entity.vertices[0].x, entity.vertices[0].y, entity.vertices[0].z || 0),
                new THREE.Vector3(entity.vertices[1].x, entity.vertices[1].y, entity.vertices[1].z || 0),
              ];
              const geometry = new THREE.BufferGeometry().setFromPoints(points);
              mesh = new THREE.Line(geometry, material);
              group.add(mesh);
            } else if (entity.type === "CIRCLE") {
              const curve = new THREE.EllipseCurve(
                entity.center.x, entity.center.y,
                entity.radius, entity.radius,
                0, 2 * Math.PI,
                false, 0
              );
              const points = curve.getPoints(50);
              const geometry = new THREE.BufferGeometry().setFromPoints(
                points.map(p => new THREE.Vector3(p.x, p.y, entity.center.z || 0))
              );
              const material = new THREE.LineBasicMaterial({ 
                color: entity.color ? new THREE.Color(entity.color) : 0x3b82f6 
              });
              mesh = new THREE.Line(geometry, material);
              group.add(mesh);
            } else if (entity.type === "ARC") {
              const startAngle = entity.startAngle * (Math.PI / 180);
              const endAngle = entity.endAngle * (Math.PI / 180);
              const curve = new THREE.EllipseCurve(
                entity.center.x, entity.center.y,
                entity.radius, entity.radius,
                startAngle, endAngle,
                false, 0
              );
              const points = curve.getPoints(50);
              const geometry = new THREE.BufferGeometry().setFromPoints(
                points.map(p => new THREE.Vector3(p.x, p.y, entity.center.z || 0))
              );
              const material = new THREE.LineBasicMaterial({ 
                color: entity.color ? new THREE.Color(entity.color) : 0x3b82f6 
              });
              mesh = new THREE.Line(geometry, material);
              group.add(mesh);
            }

            if (mesh) {
              meshMap.set(entityId, mesh);
            }
          });

          scene.add(group);

          // Calculate bounding box to fit camera
          const box = new THREE.Box3().setFromObject(group);
          const center = box.getCenter(new THREE.Vector3());
          const size = box.getSize(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z);
          const fov = camera.fov * (Math.PI / 180);
          let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
          cameraZ *= 1.5; // Add some padding

          camera.position.set(center.x, center.y, center.z + cameraZ);
          camera.lookAt(center);
          controls.target.copy(center);
          controls.update();

          meshMapRef.current = meshMap;

          // Notify parent component
          onParsed(scene, camera, renderer, parsedEntities);
        }
      } catch (error) {
        console.error("Error parsing DXF:", error);
      }
    };

    reader.readAsText(file);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !camera || !renderer) return;
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [file, onParsed]);

  // Update visibility based on visibleEntities prop
  useEffect(() => {
    if (!visibleEntities) return;

    meshMapRef.current.forEach((mesh, entityId) => {
      mesh.visible = visibleEntities.includes(entityId);
    });

    if (rendererRef.current && sceneRef.current && cameraRef.current) {
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    }
  }, [visibleEntities]);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-[600px] rounded-lg border border-border bg-card overflow-hidden shadow-technical"
    />
  );
};
