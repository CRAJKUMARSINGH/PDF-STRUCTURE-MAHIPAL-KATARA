import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Layers } from "lucide-react";

export interface DXFEntity {
  id: string;
  type: string;
  layer?: string;
  visible: boolean;
}

interface ObjectSelectorProps {
  entities: DXFEntity[];
  onToggleEntity: (id: string) => void;
  onToggleAll: (visible: boolean) => void;
}

export const ObjectSelector = ({
  entities,
  onToggleEntity,
  onToggleAll,
}: ObjectSelectorProps) => {
  const visibleCount = entities.filter((e) => e.visible).length;
  const allVisible = visibleCount === entities.length;

  return (
    <div className="bg-card rounded-xl p-6 shadow-md border border-border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Layers className="w-5 h-5 text-primary" />
          Objects ({visibleCount}/{entities.length})
        </h3>
        <div className="flex items-center gap-2">
          <Checkbox
            id="toggle-all"
            checked={allVisible}
            onCheckedChange={(checked) => onToggleAll(checked as boolean)}
          />
          <label
            htmlFor="toggle-all"
            className="text-sm font-medium cursor-pointer"
          >
            All
          </label>
        </div>
      </div>

      <ScrollArea className="h-[200px] pr-4">
        <div className="space-y-2">
          {entities.map((entity) => (
            <div
              key={entity.id}
              className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Checkbox
                  id={entity.id}
                  checked={entity.visible}
                  onCheckedChange={() => onToggleEntity(entity.id)}
                />
                <div>
                  <label
                    htmlFor={entity.id}
                    className="text-sm font-medium cursor-pointer"
                  >
                    {entity.type}
                  </label>
                  {entity.layer && (
                    <p className="text-xs text-muted-foreground">
                      Layer: {entity.layer}
                    </p>
                  )}
                </div>
              </div>
              <Badge variant="secondary" className="text-xs">
                {entity.type}
              </Badge>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};
