import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import * as api from "../api";
import { useState, useEffect } from "react";
import { CreateLinkDialog } from "@/components/CreateLinkDialog";
import type { User, Link } from "../types";
import { UpdateLinkDialog } from "@/components/UpdateLinkDialog";
import { DeleteLinkDialog } from "@/components/DeleteLinkDialog";
import { useNavigate } from "react-router-dom";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Menu } from "lucide-react";

const HomePage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [links, setLinks] = useState<Link[]>([]);

  const onCreateLink = async ({ url }: { url: string | null }) => {
    let resp: Response;

    try {
      resp = await api.createLink({ url: url });
    }
    catch (error) {
      console.error(error)
      if (error instanceof Error) {
        toast.error(error.message);
      }
      else {
        toast.error('Unexpected Error')
      }
      return;
    }

    const data = await resp.json();

    if (!resp.ok) {
      if (resp.status == 401) {
        navigate("/login");
        return;
      }
      if (resp.status == 422) {
        const message =
          data.detail
            ?.map((item: any) => `(${item.loc.at(-1)}) ${item.msg}`)
            .join("\n") ?? resp.statusText;

        throw new Error(message);
      }

      toast.error(data?.detail ?? resp.statusText);
      return;
    }

    setLinks([...links, data]);
  };

  const onUpdateLink = async ({
    id,
    url,
  }: {
    id: number | null;
    url: string | null;
  }) => {
    let resp: Response;

    try {
      resp = await api.updateLink({
        id: id,
        url: url,
      });
    }
    catch (error) {
      console.error(error)
      if (error instanceof Error) {
        toast.error(error.message)
      }
      else {
        toast.error('Unexpected error')
      }
      return;
    }

    const data = await resp.json().catch(() => null);

    if (!resp.ok) {
      if (resp.status == 401) {
        navigate("/login");
        return;
      } else if (resp.status === 422) {
        const message =
          data.detail
            ?.map((item: any) => `(${item.loc.at(-1)}) ${item.msg}`)
            .join("\n") ?? resp.statusText;
        throw new Error(message);
      }

      toast.error(data?.detail ?? resp.statusText);
      return;
    }

    setLinks(links.map((link) => (link.id === id ? data : link)));
  };

  const onDeleteLink = async ({ id }: { id: number }) => {
    let resp: Response

    try {
      resp = await api.deleteLink({ id: id });
    }
    catch (error) {
      console.error(error)
      if (error instanceof Error) {
        toast.error(error.message)
      }
      else {
        toast.error('Unexpected Error')
      }
      return;
    }

    const data = await resp.json().catch(() => null);

    if (!resp.ok) {
      if (resp.status == 401) {
        navigate("/login");
        return;
      } else if (resp.status == 422) {
        const message =
          data.detail
            ?.map((item: any) => `(${item.loc.at(-1)}) ${item.msg}`)
            .join("\n") ?? resp.statusText;
        toast.error(message);
      } else {
        if (data.detail) {
          toast.error(data.detail);
        } else {
          toast.error(resp.statusText);
        }
      }

      return;
    }

    setLinks(links.filter((link) => link.id != id));
  };

  const onLogout = async () => {
    try {
      await api.logout();
    }
    finally {
      navigate('/login', { replace: true} )
    }
  }

  useEffect(() => {
    const loadLinks = async () => {
      let resp: Response;

      try {
        resp = await api.listLinks();
      }
      catch (error) {
        console.error(error)
        if (error instanceof Error) {
          toast.error(error.message);
        }
        else {
          toast.error('Unexpected Error');
        }
        return;
      }

      if (!resp.ok) {
        if (resp.status == 401) {
          navigate("/login");
          return;
        }
        toast.error(resp.statusText);
        return;
      }

      setLinks((await resp.json()).links);
    };

    const loadUser = async () => {
      let resp: Response;

      try {
        resp = await api.me();
      }
      catch (error) {
        console.error(error)
        if (error instanceof Error) {
          toast.error(error.message)
        }
        else {
          toast.error('Unexpected Error');
        }
        return;
      }

      if (!resp.ok) {
        if (resp.status === 401) {
            navigate("/login");
            return;
        }
        toast.error(resp.statusText)
        return;
      }

      setUser(await resp.json());
    }

    const load = async () => {
        await Promise.all([loadUser(), loadLinks()])
    }

    load();
  }, [navigate]);

  return (
    <main className="min-h-screen bg-slate-100 flex flex-col">
      <header className="h-14 bg-white border-b px-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">LinkForge</h1>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="p-2 rounded-md hover:bg-slate-100">
              <Menu className="h-5 w-5" />
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="truncate">
              {user?.email}
            </DropdownMenuLabel>

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={onLogout}>
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </header>
      <section className="p-8">
        <h1 className="text-xl font-bold text-center">Links</h1>
        <div className="flex justify-end">
          <CreateLinkDialog onConfirm={onCreateLink}></CreateLinkDialog>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Short URL</TableHead>
              <TableHead>URL</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {links.length > 0 ? (
              links.map((link) => (
                <TableRow>
                  <TableCell className="font-medium">
                    <a
                      href={link.short_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline"
                    >
                      {link.short_url}
                    </a>
                  </TableCell>
                  <TableCell className="font-medium">
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline"
                    >
                      {link.url}
                    </a>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <UpdateLinkDialog
                        link={link}
                        onConfirm={onUpdateLink}
                      ></UpdateLinkDialog>
                      <DeleteLinkDialog
                        link={link}
                        onConfirm={onDeleteLink}
                      ></DeleteLinkDialog>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={3}
                  className="text-center text-muted-foreground"
                >
                  No links added
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </section>
    </main>
  );
};

export default HomePage;
