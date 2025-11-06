import { useState } from "react";
import { DXFUploader } from "@/components/DXFUploader";
import { DXFViewer } from "@/components/DXFViewer";
import { ObjectSelector, DXFEntity } from "@/components/ObjectSelector";
import { Button } from "@/components/ui/button";
import { FileDown, Loader2, FileCode } from "lucide-react";
import { jsPDF } from "jspdf";
import { toast } from "sonner";
import * as THREE from "three";

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [entities, setEntities] = useState<DXFEntity[]>([]);
  const [viewerData, setViewerData] = useState<{
    scene: THREE.Scene;
    camera: THREE.Camera;
    renderer: THREE.WebGLRenderer;
  } | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setIsProcessing(true);
  };

  const handleParsed = (
    scene: THREE.Scene,
    camera: THREE.Camera,
    renderer: THREE.WebGLRenderer,
    parsedEntities: DXFEntity[]
  ) => {
    setViewerData({ scene, camera, renderer });
    setEntities(parsedEntities);
    setIsProcessing(false);
  };

  const handleToggleEntity = (id: string) => {
    setEntities((prev) =>
      prev.map((entity) =>
        entity.id === id ? { ...entity, visible: !entity.visible } : entity
      )
    );
  };

  const handleToggleAll = (visible: boolean) => {
    setEntities((prev) =>
      prev.map((entity) => ({ ...entity, visible }))
    );
  };

  const visibleEntityIds = entities
    .filter((e) => e.visible)
    .map((e) => e.id);

  const handleConvertToPDF = async () => {
    if (!viewerData) {
      toast.error("Please load a DXF file first");
      return;
    }

    const visibleCount = entities.filter((e) => e.visible).length;
    if (visibleCount === 0) {
      toast.error("Please select at least one object to convert");
      return;
    }

    try {
      setIsProcessing(true);
      toast.info("Converting to PDF...");

      const { renderer, scene, camera } = viewerData;

      // Render the scene
      renderer.render(scene, camera);

      // Get canvas data
      const canvas = renderer.domElement;
      const imgData = canvas.toDataURL("image/png");

      // Create PDF
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? "landscape" : "portrait",
        unit: "px",
        format: [canvas.width, canvas.height],
      });

      pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);

      // Save PDF
      const fileName = selectedFile
        ? selectedFile.name.replace(/\.[^/.]+$/, ".pdf")
        : "drawing.pdf";
      pdf.save(fileName);

      toast.success(`PDF generated with ${visibleCount} object(s)!`);
    } catch (error) {
      console.error("Error converting to PDF:", error);
      toast.error("Failed to convert to PDF");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-hero">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-primary/10 rounded-xl">
              <FileCode className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              DXF to PDF Converter
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Convert your AutoCAD DXF files to PDF with precision. Upload, preview,
            and download in seconds.
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Upload Section */}
          <section className="bg-card rounded-2xl p-8 shadow-lg border border-border">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold">
                1
              </div>
              Upload DXF File
            </h2>
            <DXFUploader
              onFileSelect={handleFileSelect}
              isProcessing={isProcessing}
            />
          </section>

          {/* Preview Section */}
          {selectedFile && (
            <section className="bg-card rounded-2xl p-8 shadow-lg border border-border animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold">
                    2
                  </div>
                  Preview & Convert
                </h2>
                <Button
                  onClick={handleConvertToPDF}
                  disabled={isProcessing || !viewerData}
                  size="lg"
                  className="shadow-md hover:shadow-lg transition-all"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <FileDown className="w-5 h-5 mr-2" />
                      Download PDF
                    </>
                  )}
                </Button>
              </div>

              <DXFViewer
                file={selectedFile}
                onParsed={handleParsed}
                visibleEntities={visibleEntityIds}
              />

              {entities.length > 0 && (
                <div className="mt-6">
                  <ObjectSelector
                    entities={entities}
                    onToggleEntity={handleToggleEntity}
                    onToggleAll={handleToggleAll}
                  />
                </div>
              )}

              <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong>Tip:</strong> Use your mouse to rotate, zoom, and pan the
                  3D view. The PDF will capture the current view.
                </p>
              </div>
            </section>
          )}

          {/* Features Section */}
          <section className="grid md:grid-cols-3 gap-6 mt-12">
            {[
              {
                title: "Fast Conversion",
                description: "Convert DXF files to PDF instantly in your browser",
                icon: "⚡",
              },
              {
                title: "3D Preview",
                description: "Interactive 3D preview with zoom, pan, and rotate",
                icon: "🎯",
              },
              {
                title: "No Upload Required",
                description: "All processing happens locally in your browser",
                icon: "🔒",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-card rounded-xl p-6 shadow-md border border-border hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
              >
                <div className="text-4xl mb-3">{feature.icon}</div>
                <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </section>
        </div>
      </div>
    </div>
  );
};

export default Index;
