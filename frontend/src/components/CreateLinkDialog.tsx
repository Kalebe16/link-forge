// components/CreateLinkDialog.tsx

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

type CreateLinkDialogProps = {
  onConfirm: ({ url }: { url: string | null }) => Promise<void>;
};

export const CreateLinkDialog = (props: CreateLinkDialogProps) => {
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
        <Button className="cursor-pointer">Add</Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add link</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-2">
          <Field>
            <FieldLabel htmlFor="url">URL</FieldLabel>
            <Input ref={urlInput} id="url" type="text" />
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
