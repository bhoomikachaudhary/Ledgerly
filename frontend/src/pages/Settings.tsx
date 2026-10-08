import { useState } from "react";

import { Layout } from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import { useCategories, useCreateCategory } from "@/hooks/useCategories";

export function Settings() {
  const { user } = useAuth();
  const { data: categories } = useCategories();
  const createCategory = useCreateCategory();
  const [newCategoryName, setNewCategoryName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const onAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;
    setError(null);
    try {
      await createCategory.mutateAsync({ name: newCategoryName.trim() });
      setNewCategoryName("");
    } catch {
      setError("You already have a category with that name.");
    }
  };

  return (
    <Layout>
      <h2 className="font-display text-2xl mb-6">Settings</h2>

      <section className="mb-10">
        <h3 className="text-xs uppercase tracking-wide text-ink-soft mb-3">Account</h3>
        <div className="border border-rule px-5 py-4 text-sm space-y-1">
          <p>{user?.name}</p>
          <p className="text-ink-soft">{user?.email}</p>
        </div>
      </section>

      <section>
        <h3 className="text-xs uppercase tracking-wide text-ink-soft mb-3">Categories</h3>
        <div className="divide-y divide-rule-soft mb-4">
          {categories?.map((category) => (
            <div key={category.id} className="flex items-center gap-2 py-2.5 text-sm">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: category.color }} />
              {category.name}
            </div>
          ))}
        </div>

        <form onSubmit={onAddCategory} className="flex gap-3">
          <input
            type="text"
            className="field-input"
            placeholder="New category name"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
          />
          <button type="submit" className="btn-secondary whitespace-nowrap">
            Add category
          </button>
        </form>
        {error && <p className="field-error">{error}</p>}
      </section>
    </Layout>
  );
}
