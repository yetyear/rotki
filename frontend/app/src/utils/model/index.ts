import { kebabCase } from 'lodash-es';
import type { Ref, WritableComputedRef } from 'vue';

export function usePropVModel<
  P extends object,
  K extends keyof P,
  S extends P[K] extends object ? keyof P[K] : never,
  Name extends string,
>(props: P, key: K, subKey: S, emit?: (name: Name, ...args: any[]) => void): WritableComputedRef<P[K][S]> {
  const eventName = (
    key === 'value' ? 'input' : `update:${kebabCase(key.toString())}`
  ) as Name;
  return computed({
    get() {
      return props[key][subKey];
    },
    set(value: P[K][S]) {
      emit?.(eventName, { ...props[key], [subKey]: value });
    },
  });
}

export function useSimplePropVModel<
  T,
  P extends { value: T },
  S extends P['value'] extends object ? keyof P['value'] : never,
  Name extends string,
>(props: P, subKey: S, emit?: (name: Name, ...args: any[]) => void): WritableComputedRef<P['value'][S]> {
  return usePropVModel(props, 'value', subKey, emit);
}

export function useSimpleVModel<T, P extends { value: T }, Name extends string>(props: P, emit?: (name: Name, ...args: any[]) => void): WritableComputedRef<P['value']> {
  return useVModel(props, 'value', emit, {
    eventName: 'input',
  });
}

/**
 * Like useVModel but event is update:kebab-case
 * @param props
 * @param key
 * @param emit
 */
export function useKebabVModel<
  P extends object,
  K extends keyof P,
  Name extends string,
>(props: P, key: K, emit?: (name: Name, ...args: any[]) => void): WritableComputedRef<P[K]> {
  return useVModel(props, key, emit, {
    eventName: `update:${kebabCase(key.toString())}`,
  });
}

export function useRefPropVModel<P extends object, K extends keyof P>(obj: Ref<P>, key: K): WritableComputedRef<P[K]> {
  return computed<P[K]>({
    get() {
      return get(obj)[key];
    },
    set(value?: P[K]) {
      set(obj, {
        ...get(obj),
        [key]: value,
      });
    },
  });
}
