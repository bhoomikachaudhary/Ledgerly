interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="border border-dashed border-rule py-14 px-6 text-center">
      <p className="font-display text-lg text-ink mb-1">{title}</p>
      <p className="text-sm text-ink-soft mb-4">{description}</p>
      {action}
    </div>
  );
}
