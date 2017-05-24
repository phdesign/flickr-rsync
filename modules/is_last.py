from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def is_last(source):
    def subscribe(observer):
        value = [None]
        seen_value = [False]

        def on_next(x):
            if seen_value[0]:
                observer.on_next((value[0], False))
            value[0] = x
            seen_value[0] = True

        def on_completed():
            if seen_value[0]:
                observer.on_next((value[0], True))
            observer.on_completed()

        return source.subscribe(on_next, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)

