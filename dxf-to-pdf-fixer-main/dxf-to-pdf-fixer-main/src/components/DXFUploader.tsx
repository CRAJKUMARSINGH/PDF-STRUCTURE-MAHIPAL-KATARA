import { useCallback, useState } from "react";
import { Upload, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface DXFUploaderProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export const DXFUploader = ({ onFileSelect, isProcessing }: DXFUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const validateFile = (file: File): boolean => {
    const validExtensions = [".dxf"];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf("."));
    
    if (!validExtensions.includes(fileExtension)) {
      toast.error("Invalid file type. Please upload a DXF file.");
      return false;
    }
    
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      toast.error("File is too large. Maximum size is 50MB.");
      return false;
    }
    
    return true;
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
      toast.success(`${file.name} loaded successfully`);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="w-full">
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300",
          isDragging 
            ? "border-primary bg-primary/5 scale-[1.02]" 
            : "border-border hover:border-primary/50 hover:bg-muted/30",
          isProcessing && "opacity-50 pointer-events-none"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".dxf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isProcessing}
        />
        
        <div className="flex flex-col items-center gap-4">
          <div className={cn(
            "p-6 rounded-full bg-gradient-to-br transition-all duration-300",
            isDragging 
              ? "from-primary to-primary/70 scale-110" 
              : "from-primary/10 to-primary/5"
          )}>
            <Upload className={cn(
              "w-12 h-12 transition-colors",
              isDragging ? "text-primary" : "text-muted-foreground"
            )} />
          </div>
          
          <div>
            <h3 className="text-xl font-semibold mb-2">
              {selectedFile ? "File Selected" : "Drop your DXF file here"}
            </h3>
            <p className="text-muted-foreground">
              {selectedFile ? (
                <span className="flex items-center gap-2 justify-center">
                  <FileText className="w-4 h-4" />
                  {selectedFile.name}
                </span>
              ) : (
                "or click to browse"
              )}
            </p>
          </div>
          
          {selectedFile && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={(e) => {
                e.stopPropagation();
                clearFile();
              }}
            >
              <X className="w-4 h-4 mr-2" />
              Clear
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
