import { forwardRef } from 'react'
import type { HTMLAttributes } from 'react'

interface TableProps extends HTMLAttributes<HTMLTableElement> {}

export const Table = forwardRef<HTMLTableElement, TableProps>(
  ({ className = '', children, ...props }, ref) => (
    <div className="overflow-x-auto">
      <table
        ref={ref}
        className={`min-w-full divide-y divide-[var(--color-border)] ${className}`}
        {...props}
      >
        {children}
      </table>
    </div>
  )
)

Table.displayName = 'Table'

interface TableHeaderProps extends HTMLAttributes<HTMLTableSectionElement> {}

export const TableHeader = forwardRef<HTMLTableSectionElement, TableHeaderProps>(
  ({ className = '', children, ...props }, ref) => (
    <thead
      ref={ref}
      className={`bg-gray-50 ${className}`}
      {...props}
    >
      {children}
    </thead>
  )
)

TableHeader.displayName = 'TableHeader'

interface TableBodyProps extends HTMLAttributes<HTMLTableSectionElement> {}

export const TableBody = forwardRef<HTMLTableSectionElement, TableBodyProps>(
  ({ className = '', children, ...props }, ref) => (
    <tbody
      ref={ref}
      className={`bg-white divide-y divide-[var(--color-border)] ${className}`}
      {...props}
    >
      {children}
    </tbody>
  )
)

TableBody.displayName = 'TableBody'

interface TableRowProps extends HTMLAttributes<HTMLTableRowElement> {}

export const TableRow = forwardRef<HTMLTableRowElement, TableRowProps>(
  ({ className = '', children, ...props }, ref) => (
    <tr
      ref={ref}
      className={`hover:bg-gray-50 ${className}`}
      {...props}
    >
      {children}
    </tr>
  )
)

TableRow.displayName = 'TableRow'

interface TableHeadProps extends HTMLAttributes<HTMLTableCellElement> {}

export const TableHead = forwardRef<HTMLTableCellElement, TableHeadProps>(
  ({ className = '', children, ...props }, ref) => (
    <th
      ref={ref}
      className={`px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider ${className}`}
      {...props}
    >
      {children}
    </th>
  )
)

TableHead.displayName = 'TableHead'

interface TableCellProps extends HTMLAttributes<HTMLTableCellElement> {}

export const TableCell = forwardRef<HTMLTableCellElement, TableCellProps>(
  ({ className = '', children, ...props }, ref) => (
    <td
      ref={ref}
      className={`px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-primary)] ${className}`}
      {...props}
    >
      {children}
    </td>
  )
)

TableCell.displayName = 'TableCell'