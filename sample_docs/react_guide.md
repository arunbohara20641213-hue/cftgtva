React 18 and Modern Frontend Development

## What is React?

React is a JavaScript library for building user interfaces with reusable components. Created by Facebook, it uses a virtual DOM for efficient updates.

## Core Concepts

### Components
Building blocks of React apps. Functional components are modern standard:

```jsx
function Welcome() {
  return <h1>Hello, React!</h1>;
}

export default Welcome;
```

### JSX
JavaScript XML syntax makes React code readable:

```jsx
const element = (
  <div>
    <h1>Title</h1>
    <p>Description</p>
  </div>
);
```

Compiles to:
```javascript
const element = React.createElement('div', null,
  React.createElement('h1', null, 'Title'),
  React.createElement('p', null, 'Description')
);
```

### State and Props

**Props**: Immutable data passed to components
```jsx
function Greeting({ name, age }) {
  return <p>Hello {name}, age {age}</p>;
}

<Greeting name="John" age={30} />
```

**State**: Mutable data inside component
```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### Hooks
Functions that let you use state in functional components:

**useState**: Manage component state
```jsx
const [email, setEmail] = useState('');
```

**useEffect**: Handle side effects (API calls, subscriptions)
```jsx
useEffect(() => {
  // Runs after component renders
  fetchData();
}, [dependency]); // Runs when dependency changes
```

**useContext**: Access context values
```jsx
const user = useContext(AuthContext);
```

**useReducer**: Complex state management
```jsx
const [state, dispatch] = useReducer(reducer, initialState);
```

**useCallback**: Memoize callback functions
```jsx
const handleClick = useCallback(() => {
  doSomething();
}, [dependency]);
```

**useMemo**: Memoize expensive computations
```jsx
const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(data);
}, [data]);
```

## React 18 Features

### Automatic Batching
Multiple state updates in event handlers batched together:

```jsx
function handleClick() {
  setName('John');        // Batched
  setAge(30);             // Batched
  // Component re-renders once, not twice
}
```

### Transitions
Mark non-urgent updates with startTransition:

```jsx
const [isPending, startTransition] = useTransition();

function handleSearch(query) {
  startTransition(() => {
    setQuery(query);  // Non-blocking update
  });
}

return isPending ? <Spinner /> : <Results />;
```

### Suspense for Data Fetching
Suspense now works with data fetching (experimental):

```jsx
function PostPage({ postId }) {
  return (
    <Suspense fallback={<Loading />}>
      <Post postId={postId} />
    </Suspense>
  );
}

function Post({ postId }) {
  const post = use(fetchPost(postId)); // Throws promise, Suspense catches it
  return <h1>{post.title}</h1>;
}
```

## State Management

### Context API
Built-in solution for prop drilling:

```jsx
const UserContext = createContext();

function App() {
  const [user, setUser] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      <Header />
      <MainContent />
    </UserContext.Provider>
  );
}

// Inside component
const { user } = useContext(UserContext);
```

### Popular Libraries
- **Redux**: Centralized state management (for large apps)
- **Zustand**: Simple state management
- **Jotai**: Primitive state management
- **Recoil**: Experimental state management by Facebook

## Performance Optimization

### Code Splitting
Load code only when needed:

```jsx
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Memoization
Prevent unnecessary re-renders:

```jsx
const ExpensiveComponent = memo(function List({ items }) {
  return items.map(item => <Item key={item.id} item={item} />);
});
```

### Virtual Lists
For long lists, render only visible items:

```jsx
import { FixedSizeList } from 'react-window';

function LongList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={35}
    >
      {({ index, style }) => <div style={style}>{items[index]}</div>}
    </FixedSizeList>
  );
}
```

## Common Libraries

### UI Components
- Material-UI: Full component library
- Chakra UI: Accessible components
- Shadcn/ui: Copyable component library

### Routing
- React Router: Client-side routing
- Next.js: Framework with built-in routing

### HTTP Client
- Axios: Promise-based HTTP client
- React Query: Data fetching and caching
- SWR: React Hooks for data fetching

### Form Handling
- React Hook Form: Performant form handling
- Formik: Popular form management

## Testing

### Jest
Testing framework (included with Create React App):

```jsx
describe('Counter', () => {
  test('increments count', () => {
    const { getByRole } = render(<Counter />);
    const button = getByRole('button');
    fireEvent.click(button);
    expect(getByText('Count: 1')).toBeInTheDocument();
  });
});
```

### React Testing Library
User-focused testing:

```jsx
test('form submission', async () => {
  render(<LoginForm />);
  const emailInput = screen.getByLabelText('Email');
  const submitButton = screen.getByRole('button', { name: /submit/i });
  
  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.click(submitButton);
  
  await waitFor(() => {
    expect(screen.getByText('Login successful')).toBeInTheDocument();
  });
});
```

## Best Practices

1. **Keep components small**: Single responsibility
2. **Prop drilling solution**: Use Context or state management
3. **Avoid inline functions**: Use useCallback for callbacks
4. **Optimize re-renders**: Use React.memo and useMemo
5. **Handle errors**: Error boundaries for graceful degradation
6. **Accessibility**: Use semantic HTML, ARIA labels
7. **Performance**: Code splitting, lazy loading, image optimization

## Conclusion

React 18 provides powerful tools for building scalable, performant user interfaces. Master the fundamentals, and you can build anything from simple widgets to complex applications.
