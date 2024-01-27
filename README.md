# AI Agents: Testing OpenAI Tools

A simple agent testing a bunch of OpenAI conforming tools.

## Deployed solution

[Playground demo, hosted on Fly.io](https://agent-functions-test.fly.dev/agent/playground/)

## How to run locally

First of all you need [Poetry](https://python-poetry.org/docs/#installation).
```
> pip install poetry
```

An account on [Free Weather API](https://www.weatherapi.com/), for the weather tool. 

And an OpenAI API key.

Then clone the repo and:
```
> git clone https://github.com/tomasellis/agent_tools_test
> cd agent_tools_test
```

Make a .env including:
```
OPENAI_API_KEY=****
WEATHER_API_KEY=****
```

```
> pnpm dev:python
> pnpm 
```

### How to run tests
```
> npm run test
```

## Take home requirements
- ✅ Use React and TypeScript
  - App scaffolded with `npm create vite@latest infinite-scroll -- --template react-ts`
- ✅ The UI/UX should be intuitive and easy to use
  - Included HomeVision branding taken from the URL given
  - Chose a simple, high contrast design, with support for mobile devices
  - Chose to communicate errors after a few failed requests with a toast component
  - Included a 'scroll to top' button with smooth transitions for a pleasant navigation
- ✅ Display an infinite scroll of the houses and use all of the data returned
  - Implemented an infinite scroll which communicates loading and (hypothetical) end of list cases
  - All the data returned (but the ID) is displayed. The ID is used as a React key
- ✅ Write tests where you think appropriate
  - ~~I chose not to include tests in this excercise as I didn't think it'd provide value for the use cases implemented~~
  - Set up testing with Vitest
  - Included tests for InfiniteScroll component's integrity
  - Included tests for HomeListing full address display at all times
- ✅ Bonus points:
  - ✅ Deploy and host it in the cloud so we can access it via a public URL
    - Deployed at Vercel
  - ✅ Implement your own infinite scroll component
    - Component can be found at `src/components/InfiniteScroll.tsx`

## Observations about the stack
- About [TailwindCSS](https://tailwindcss.com/docs/utility-first)
  - A utility-first CSS framework packed with classes that can be composed to build any design, directly in your markup
  - Why I chose it: I've worked with it beofre, and it's a fast way of having beautiful results without the commitment to a component library
- About [`shadcn/ui`](https://ui.shadcn.com/)
  - A family of customizable, opinionated components from the Vercel team; Start with some sensible defaults, then customize the components to your needs. [It's not a component library](https://ui.shadcn.com/docs)
  - Why I chose it: I really liked some of their components and the default styling for this project (which is also done in TailwindCSS). You'll notice these are located inside `src/components/ui`, while my own components are in `src/components`
- About [Vite](https://vitejs.dev/guide/)/[Vitest](https://vitest.dev/)
  - Next generation frontend tooling optimized for developer experience
  - Why I chose it: at the time of starting this project, while being a performant build tool, it provided the simplest, most up-to-date scaffold for a `react-ts` app. Following the decision, Vitest was the go-to integration for UI testing
- About [SWR](https://swr.vercel.app/)
  - React hooks for data fetching (i.e 'Stale while revalidate') by the Vercel team
  - Why I chose it: this is a comprehensive implementation of the use cases around asynchronous state management, exposed through really simple outputs. In this excercise, it makes error handling and loading states simple to work with

### Other observations
- About [IntersectionObserver](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
  - The Intersection Observer API provides a way to asynchronously observe changes in the intersection of a target element.
  - Why I chose it: the first intuition around implementing the InfiniteScroll component came to me with this in mind, and I really liked the simplicity of the later implementation. This API is available in all modern browsers since around 2016/17.