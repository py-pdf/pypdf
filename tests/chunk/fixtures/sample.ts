/** Module doc. */
import { Thing } from "./thing";

export class PublicClass extends Base implements Foo {
  /** Method doc. */
  publicMethod(): void {}

  _privateMethod(): void {}
}

export interface PublicInterface extends Bar {
  field: string;
}

export type PublicType = string;

export function publicFunction(): void {}

const publicArrow = () => {};

export class _PrivateClass {}
