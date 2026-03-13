import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { Link } from "../types";

type UpdateLinkDialogProps = {
  link: Link;
  onConfirm: ({
    id,
    url,
  }: {
    id: number | null;
    url: string | null;
  }) => Promise<void>;
};

const UpdateLinkDialog = (props: UpdateLinkDialogProps) => {
  const urlInput = useRef<HTMLInputElement | null>(null);

  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open);

        if (!open) {
          setError("");
        }
      }}
    >
      <DialogTrigger asChild>
        <Button className="cursor-pointer" variant="outline" size="sm">
          Edit
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit link</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-2">
          <Field>
            <FieldLabel htmlFor={`update-url-${props.link.id}`}>URL</FieldLabel>

            <Input
              ref={urlInput}
              id={`update-url-${props.link.id}`}
              type="text"
              defaultValue={props.link.url}
            />
          </Field>

          {error && (
            <Alert variant="destructive">
              <AlertDescription className="whitespace-pre-line">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex justify-end gap-2">
            <Button
              className="cursor-pointer"
              variant="outline"
              onClick={() => setIsOpen(false)}
            >
              Cancel
            </Button>

            <Button
              className="cursor-pointer"
              onClick={async () => {
                try {
                  await props.onConfirm({
                    id: props.link.id,
                    url: urlInput.current?.value || null,
                  });

                  setIsOpen(false);
                } catch (error) {
                  if (error instanceof Error) {
                    setError(error.message);
                  }
                }
              }}
            >
              Confirm
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export { UpdateLinkDialog };
