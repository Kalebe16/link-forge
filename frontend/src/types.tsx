type User = {
  id: number;
  email: string;
  created_at: string;
};

type Link = {
  id: number;
  url: string;
  short_url: string;
};

export type { User, Link };
